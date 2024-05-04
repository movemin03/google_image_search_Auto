# Built-in imports
import os
import time
from datetime import datetime, timedelta
import urllib.request

# Third-party imports
import shutil
import pandas as pd
import numpy as np
import requests
from PIL import Image
import cv2
from io import BytesIO
from skimage.metrics import structural_similarity as ssim  # pyinstaller 사용 시, scikit-image 로 hidden-import 할 것
from PIL.ExifTags import TAGS
from multiprocessing import Pool, cpu_count, freeze_support
from google.cloud import vision
import openpyxl

def check_internet():
    try:
        urllib.request.urlopen('http://www.google.com', timeout=5)
        print("인터넷 연결 상태: 연결됨")
    except urllib.error.URLError:
        print("인터넷 연결 상태: 연결되지 않음, 인터넷 연결 후 재실행")
        a = input()
        exit()

def chk_dest_dir(dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        # 대상 디렉토리가 비어있지 않다면
        if os.listdir(dest_dir):
            shutil.rmtree(dest_dir)
            os.makedirs(dest_dir)


def maping_files(source_dir):
    index_table = []
    for foldername, subfolders, filenames in os.walk(source_dir, topdown=True):
        # 하위 폴더를 제외하도록 설정
        subfolders.clear()
        idx = 1
        # 이제 해당 폴더에 대해서만 반복문 실행
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
                # 여기서 필요한 작업을 수행
                file_path = os.path.join(foldername, filename)
                index_table.append((file_path, idx))
                idx += 1
    return index_table

def compress_image(image_path, output_folder, idx, fixed_height=2160):
    img = Image.open(image_path)
    width, height = img.size
    new_width = int(width * (fixed_height / height))
    new_height = fixed_height
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    resized_img.convert("RGB").save(f"{output_folder}\\{idx}.jpg", quality=90, optimize=True)


# 멀티프로세싱을 이용한 이미지 압축 함수
def compress_images_with_multiprocessing(index_table, dest_dir):
    num_processes = cpu_count()  # 사용 가능한 CPU 코어 수를 가져옵니다.
    with Pool(processes=num_processes) as pool:
        pool.starmap(compress_image, [(file_path, dest_dir, idx, 2160) for file_path, idx in index_table])

def detect_web(path):
    full_match_url = []
    full_match_img = []
    visually_similar_img = ""

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.web_detection(image=image)
    annotations = response.web_detection

    if annotations.pages_with_matching_images:
        full_matching_cnt = 0
        for page in annotations.pages_with_matching_images:
            if full_matching_cnt == 3:
                break
            if page.full_matching_images:
                full_matching_cnt += 1
                full_match_url.append(page.url)
                full_match_img.append(page.full_matching_images[0].url)

    if annotations.visually_similar_images:
        visually_similar_cnt = 0
        for image in annotations.visually_similar_images:
            if visually_similar_cnt == 3:
                break
            visually_similar_cnt += 1
            visually_similar_img = str(image.url)

    return full_match_url, full_match_img, visually_similar_img


def requests_to_image(searched_string):
    response = requests.get(searched_string)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def calculate_ssim(image1, image2):
    # 이미지를 그레이스케일로 변환
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 유사도 계산
    (_, similarity) = ssim(gray1, gray2, full=True)
    return similarity


def image_similarity(searched_string, path):
    # 이미지 읽어오기
    image1 = requests_to_image(searched_string)
    image2 = cv2.imread(path)

    # 가로 세로 통일
    width = min(image1.shape[1], image2.shape[1])
    height = min(image1.shape[0], image2.shape[0])

    image1 = cv2.resize(image1, (width, height))
    image2 = cv2.resize(image2, (width, height))

    # 그레이 스케일로 변경
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 유사도 계산
    (_, similarity_matrix) = ssim(gray1, gray2, full=True)

    # 이미지 유사도 계산
    similarity_matrix = calculate_ssim(image1, image2)
    similarity = np.mean(similarity_matrix) * 100
    return similarity


def get_value_by_index(index_table, idx):
    for item in index_table:
        if item[1] == idx:
            return item[0]
    return None  # 인덱스에 해당하는 값이 없는 경우 None 반환

def extract_image_metadata(image_path):
    # 이미지 열기
    image = Image.open(image_path)

    # exif 데이터 추출
    exif_data = image._getexif()

    # 추출한 데이터를 저장할 딕셔너리
    metadata = {}

    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            metadata[tag_name] = value

    # 찍은 날짜, 만든 날짜, 수정한 날짜, 프로그램 이름 추출
    taken_date = metadata.get('DateTimeOriginal', "기록된 값이 없습니다")
    created_date = metadata.get('DateTime', "기록된 값이 없습니다")
    modified_date = os.path.getmtime(image_path)
    program_name = metadata.get('Software', "기록된 값이 없습니다")

    # Unix 타임스탬프를 날짜 형식으로 변환
    modified_date = datetime.fromtimestamp(modified_date)

    return taken_date, created_date, modified_date, program_name


def find_image_url(path):
    # 원본 이미지 exif 찾기
    filename_list.append(get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))
    taken_date, created_date, modified_date, program_name = extract_image_metadata(
        get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))

    taken_date_list.append(taken_date)
    created_date_list.append(created_date)
    modified_date_list.append(modified_date)
    program_name_list.append(program_name)

    print("1/2: 이미지 exif 추출 완료")

    # 유사 이미지 검색
    full_match_url, full_match_img, visually_similar_img = detect_web(path)

    if len(full_match_img) != 0:
        compare_img_unit = full_match_img[0].replace("'", "")
    elif visually_similar_img != '':
        compare_img_unit = repr(visually_similar_img).replace("'", "")
    else:
        compare_img_unit = None

    if compare_img_unit:
        print(compare_img_unit)
        similarity = image_similarity(compare_img_unit, path)
        print("2/2: 유사도 검색 완료")
    else:
        similarity = 0
        print("2/2: 유사도 검색 할 수 없습니다")

    similarity_list.append(similarity)
    full_match_url_list.append(str(full_match_url))
    full_match_img_list.append(str(full_match_img))
    visually_similar_img_list.append(visually_similar_img)

if __name__ == "__main__":
    freeze_support()
    print("*****구글 이미지로 검색 자동화 프로그램입니다*****")
    print("notice: 본 프로그램은 SSIM 방식의 유사도 평가방식을 사용합니다")
    ver = "2024-05-04"
    print("ver:", ver, "\n")
    check_internet()

    # 경로 설정
    while True:
        source_dir = input("\n사진이 들어있는 폴더 경로를 넣어주세요(put your folder path):").replace("'", "").replace('"', "")

        # 입력된 경로에 한글이 포함되어 있는지 확인
        if not any(char >= '\uac00' and char <= '\ud7a3' for char in source_dir):
            # 입력된 경로가 존재하는지 확인
            if os.path.exists(source_dir):
                # 입력된 경로가 폴더인지 파일인지 확인
                if os.path.isdir(source_dir):
                    break  # 입력된 경로가 폴더 경로일 경우 루프 종료
                else:
                    print("입력된 경로는 파일 경로입니다. 폴더 경로를 입력해주세요.")
            else:
                print("입력된 경로가 존재하지 않습니다. 다시 입력해주세요.")
        else:
            print("한글이 포함된 경로입니다. 영어 경로로 변경해주세요. 한글이 포함되어 있으면 유사도 검사를 실시할 수 없습니다")

    print("입력된 경로:", source_dir)

    # 이미지 변환 후 저장할 폴더 위치 생성
    dest_dir = source_dir + "\\converted"
    if os.path.exists(dest_dir):
        for file_name in os.listdir(dest_dir):
            file_path = os.path.join(dest_dir, file_name)  # 기존 파일들 삭제
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"파일 삭제에 오류가 있습니다 {file_path}: {e}")
                continue
    else:
        os.makedirs(dest_dir)

    # 이미지 전처리
    print("\n이미지 전처리 중입니다\n이미지가 많을 시 처리에 시간이 걸릴 수 있습니다")
    print("별도의 안내가 있을 때까지 종료하지 마십시오\n안정된 검색을 위해 용량을 줄이고, 파일명을 변경하고 있습니다")
    index_table = maping_files(source_dir)
    compress_images_with_multiprocessing(index_table, dest_dir)
    print("이미지 전처리가 완료되었습니다. 저장폴더: ", dest_dir, "\n")

    # 크롬 브라우저 설정 및 열기
    user = os.getlogin()

    # 리스트 생성 및 초기화
    filename_list = []
    taken_date_list = []
    created_date_list = []
    modified_date_list = []
    program_name_list = []

    full_match_url_list = []
    full_match_img_list = []
    visually_similar_img_list = []
    similarity_list = []

    # converted 폴더 전체 파일 갯수 구
    file_count = len(os.listdir(dest_dir))

    # find_image_url 함수 실행
    rope = 0
    total_start_time = datetime.now()
    stacked_time = 0

    # 처리 순서를 오름차순으로 정렬
    converted_file_list = os.listdir(dest_dir)
    sorted_file_list = sorted(converted_file_list, key=lambda x: int(x.split('.')[0]))

    # 이미지 대조
    for file in sorted_file_list:
        rope += 1
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):  # 이미지 파일만 처리
            start_time = time.time()
            print(file_count, "중", rope, "항목 처리 중")
            find_image_url(dest_dir + "\\" + file)
            end_time = time.time()
            used_time = end_time - start_time
            print("처리소모 시간(s):", used_time)
            stacked_time += used_time
            stacked_time_total = stacked_time / rope * file_count + 2
            estimate_time = total_start_time + timedelta(seconds=stacked_time_total)
            print("예상 작업 종료 시간:", estimate_time, "\n")

    # 데이터프레임 생성 및 저장
    df = pd.DataFrame(
        {'파일명': filename_list, '유사도_ssim방식': similarity_list, '동일 이미지 사이트 url': full_match_url_list, '동일 이미지 원본 url': full_match_img_list, '유사 이미지 원본 url': visually_similar_img_list,
         '찍은 날짜': taken_date_list, '만든 날짜': created_date_list, '수정한 날짜': modified_date_list,
         '프로그램 이름': program_name_list})
    while True:
        try:
            df.to_excel(f"C:\\Users\\{user}\\Desktop\\img_links.xlsx", index=False)
            print("\n엑셀 파일이 성공적으로 저장되었습니다.")
            break  # 성공적으로 저장되었으므로 반복문 종료
        except Exception as e:
            print(f"엑셀 파일 저장 중 오류가 발생했습니다: {e}")
            print("img_links.xlsx 엑셀 파일이 열려있는 경우 종료해주시고 엔터하면 저장을 재시도합니다")
            a = input()
            continue  # 예외가 발생하면 다시 시도
    print("바탕화면에 img_links.xlsx 이름으로 저장되었습니다")
    print("엔터를 누르면 프로그램이 종료됩니다")

    a = input()
