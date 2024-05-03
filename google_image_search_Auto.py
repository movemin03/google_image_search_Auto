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
from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from skimage.metrics import structural_similarity as ssim  # pyinstaller 사용 시, scikit-image 로 hidden-import 할 것
from PIL.ExifTags import TAGS
from multiprocessing import Pool, cpu_count, freeze_support

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
    resized_img.save(f"{output_folder}\\{idx}.jpg", quality=90, optimize=True)


# 멀티프로세싱을 이용한 이미지 압축 함수
def compress_images_with_multiprocessing(index_table, dest_dir):
    num_processes = cpu_count()  # 사용 가능한 CPU 코어 수를 가져옵니다.
    with Pool(processes=num_processes) as pool:
        pool.starmap(compress_image, [(file_path, dest_dir, idx, 2160) for file_path, idx in index_table])


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


def find_image_url(path, rope, five_zero_four):
    def find_image_action(rope, five_zero_four):
        driver.get("https://images.google.com/")
        print("504 발생여부:", five_zero_four)

        if rope < 3 or five_zero_four == 1 or five_zero_four == 2:
            if five_zero_four == 1:
                five_zero_four += 1
            elif five_zero_four == 2:
                five_zero_four -= 2
            try:
                driver.switch_to.frame("callout")
                WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '로그아웃 상태 유지')]")))
                logout_button = driver.find_element(By.XPATH, "//button[contains(text(), '로그아웃 상태 유지')]")
                logout_button.click()
                print("로그아웃 상태 유지 창 처리 완료")
            except:
                try:
                    # Chrome으로 전환
                    WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '아니오')]")))
                    convert_chrome = driver.find_element(By.XPATH, "//button[contains(text(), '아니오')]")
                    convert_chrome.click()
                    print("크롬으로 전환 창 처리 완료")
                except:
                    pass
            print("메시지 창 점검 완료")
        driver.switch_to.default_content()
        # 구글 렌즈 접근
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]"))
        )

        while True:
            try:
                element.click()
                break
            except ElementClickInterceptedException:
                time.sleep(1)

        time.sleep(1)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.PXT6cd"))
        )
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        driver.get(path)
        action = ActionChains(driver)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        action.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        driver.switch_to.window(tabs[0])
        action.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()  # Ctrl+V 키 입력
        action.perform()

    find_image_action(rope, five_zero_four)

    # URL 갱신 확인 후 저장
    while True:
        new_url = driver.current_url
        if "https://lens.google.com/search?ep=" in new_url:
            break
        time.sleep(1)
        try:
            if driver.find_element(By.XPATH, "/html/body/p[1]/b").text == "502.":
                five_zero_four = 1
                driver.refresh()
                find_image_action(rope, five_zero_four)
        except:
            pass
        print("페이지가 이동될 때까지 대기중: 이미지 업로드가 제대로 되었는지 확인")
    url_list.append(new_url)

    filename_list.append(get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))
    taken_date, created_date, modified_date, program_name = extract_image_metadata(
        get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))

    taken_date_list.append(taken_date)
    created_date_list.append(created_date)
    modified_date_list.append(modified_date)
    program_name_list.append(program_name)

    print("1/2: 검색 url 저장 완료")
    wait.until(EC.presence_of_element_located((By.XPATH,
                                               '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/div/div[1]/div/div[1]/div[2]/span/div[1]/button/span/div')))
    target_div = driver.find_element(By.CLASS_NAME, "aah4tc")
    searched_item = target_div.find_element(By.XPATH, "./*/*/*/*/*")
    searched_string = searched_item.get_attribute("data-thumbnail-url")
    searched_url = searched_item.get_attribute("data-action-url")
    if searched_string:
        similarity = image_similarity(searched_string, path)
        print("2/2: 유사도 검색 완료")
    else:
        similarity = 0
        searched_url = ""
        print("2/2: 유사도 검색 할 수 없습니다")
    similarity_list.append(similarity)
    searched_url_list.append(searched_url)

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
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
    option = Options()
    option.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=option)
    driver.execute_script("window.open()")
    tabs = driver.window_handles
    wait = WebDriverWait(driver, 5)
    driver.switch_to.window(tabs[0])

    # 리스트 생성 및 초기화
    filename_list = []
    url_list = []
    similarity_list = []
    searched_url_list = []
    taken_date_list = []
    created_date_list = []
    modified_date_list = []
    program_name_list = []

    # converted 폴더 전체 파일 갯수 구
    file_count = len(os.listdir(dest_dir))

    # find_image_url 함수 실행
    rope = 0
    five_zero_four = 0
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
            find_image_url(dest_dir + "\\" + file, rope, five_zero_four)
            end_time = time.time()
            used_time = end_time - start_time
            print("처리소모 시간(s):", used_time)
            stacked_time += used_time
            stacked_time_total = stacked_time / rope * file_count + 2
            estimate_time = total_start_time + timedelta(seconds=stacked_time_total)
            print("예상 작업 종료 시간:", estimate_time, "\n")

    driver.quit()

    # 데이터프레임 생성 및 저장
    df = pd.DataFrame(
        {'파일명': filename_list, '구글 검색 url': url_list, '유사도_ssim방식': similarity_list, '유사 이미지 링크': searched_url_list,
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
