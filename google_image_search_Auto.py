print("구글 이미지로 검색 자동화 프로그램입니다")
print("SSIM 방식으로 유사도를 평가하고 있습니다")
import urllib.request
#인터넷 연결 체크
def check_internet():
    try:
        urllib.request.urlopen('http://www.google.com', timeout=5)
        print("인터넷 연결 상태: 연결됨")
    except urllib.error.URLError:
        print("인터넷 연결 상태: 연결되지 않음, 인터넷 연결 후 재실행")
        a = input()
        exit()

check_internet()
print("사용에 필요한 모듈을 로딩합니다. 시간이 소요될 수 있습니다")

import os
import numpy as np
import requests
from PIL import Image
import shutil
from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
import cv2
from skimage.metrics import structural_similarity as ssim
from datetime import datetime
from PIL.ExifTags import TAGS

while True:
    # 사용자로부터 경로 입력 받기
    source_dir = input("사진이 들어있는 폴더 경로를 넣어주세요(put your folder path):").replace("'", "").replace('"', "")

    # 입력된 경로에 한글이 포함되어 있는지 확인
    if not any(char >= '\uac00' and char <= '\ud7a3' for char in source_dir):
        break
    else:
        print("한글이 포함된 경로입니다. 영어 경로로 변경해주세요. 한글이 포함되어 있으면 유사도 검사를 실시할 수 없습니다")

print("입력된 경로:", source_dir)
dest_dir = source_dir + "\\converted"


def chk_dest_dir(dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        # 대상 디렉토리가 비어있지 않다면
        if os.listdir(dest_dir):
            shutil.rmtree(dest_dir)
            os.makedirs(dest_dir)
try:
    chk_dest_dir(dest_dir)
except:
    print("파일 경로가 아니라 폴더 경로를 넣어주셔야 합니다. 엔터를 누르면 프로그램이 종료됩니다")
    a = input()
    exit()

# 파일 용량 체크
def check_size(file):
    return os.path.getsize(file)

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


# 이미지 압축
def compress_image(image_path, output_folder, desired_size, idx):
    img = Image.open(image_path)
    img.save(f"{output_folder}\\{idx}.jpg", quality=90, optimize=True)

index_table = []


# 파일 처리
def process_files(source_dir, dest_dir):
    print("별도의 안내가 있을 때까지 종료하지 마십시오\n안정된 검색을 위해 용량을 줄이고, 파일명을 변경하고 있습니다")
    for foldername, subfolders, filenames in os.walk(source_dir, topdown=True):
        # 하위 폴더를 제외하도록 설정
        subfolders.clear()
        idx = 1
        # 이제 해당 폴더에 대해서만 반복문 실행
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
                # 여기서 필요한 작업을 수행
                file_path = os.path.join(foldername, filename)
                compress_image(file_path, dest_dir, 195, idx)  # 이미지 압축
                index_table.append((file_path, idx))
                idx += 1

# 실행
print("\n이미지 전처리 중입니다\n이미지가 많을 시 처리에 시간이 걸릴 수 있습니다")
process_files(source_dir, dest_dir)
print("이미지 전처리가 완료되었습니다. 저장폴더: ", dest_dir, "\n")

user = os.getlogin()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
option = Options()
option.add_argument(f"user-agent={user_agent}")
driver = webdriver.Chrome(options=option)
driver.execute_script("window.open()")
tabs = driver.window_handles
driver.switch_to.window(tabs[0])

# 리스트 초기화
filename_list = []
url_list = []
similarity_list = []
searched_url_list = []
taken_date_list = []
created_date_list = []
modified_date_list = []
program_name_list = []

wait = WebDriverWait(driver, 5)

def calculate_ssim(image1, image2):
    # 이미지를 그레이스케일로 변환
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 유사도 계산
    (_, similarity) = ssim(gray1, gray2, full=True)
    return similarity


def requests_to_image(searched_string):
    # base64 문자열을 이미지로 디코딩
    response = requests.get(searched_string)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def image_similarity(searched_string, path):
    # base64 이미지를 이미지로 변환
    base64_image = requests_to_image(searched_string)
    # 파일에서 이미지를 읽어옴
    image2 = cv2.imread(path)

    width = min(base64_image.shape[1], image2.shape[1])
    height = min(base64_image.shape[0], image2.shape[0])

    base64_image = cv2.resize(base64_image, (width, height))
    image2 = cv2.resize(image2, (width, height))

    # 이미지 유사도 계산
    similarity_matrix = calculate_ssim(base64_image, image2)
    similarity = np.mean(similarity_matrix)
    return similarity

def get_value_by_index(index_table, idx):
    for item in index_table:
        if item[1] == idx:
            return item[0]
    return None  # 인덱스에 해당하는 값이 없는 경우 None 반환

# 함수 정의
def find_image_url(path, rope):
    driver.get("https://images.google.com/")

    if rope < 3:
        try:
            driver.switch_to.frame("callout")
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '로그아웃 상태 유지')]")))
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
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]"))
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

    # URL 갱신 확인 후 저장
    while True:
        new_url = driver.current_url
        if "https://lens.google.com/search?ep=" in new_url:
            break
        time.sleep(1)
        print("페이지가 이동될 때까지 대기중: 이미지 업로드가 제대로 되었는지 확인")
    url_list.append(new_url)

    filename_list.append(get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))
    taken_date, created_date, modified_date, program_name = extract_image_metadata(get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))

    taken_date_list.append(taken_date)
    created_date_list.append(created_date)
    modified_date_list.append(modified_date)
    program_name_list.append(program_name)

    print("1/2: 검색 url 저장 완료")
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/div/div[1]/div/div[1]/div[2]/span/div[1]/button/span/div')))
    target_div = driver.find_element(By.CLASS_NAME, "aah4tc")
    searched_item = target_div.find_element(By.XPATH, "./*/*/*/*/*")
    searched_string = searched_item.get_attribute("data-thumbnail-url")
    searched_url = searched_item.get_attribute("data-action-url")
    if searched_string:
        similarity = image_similarity(searched_string, path) * 100
        print("2/2: 유사도 검색 완료\n")
    else:
        similarity = 0
        searched_url = ""
        print("2/2: 유사도 검색 할 수 없습니다\n")
    similarity_list.append(similarity)
    searched_url_list.append(searched_url)

upper_path = dest_dir

# converted 폴더 전체 파일 갯수 구하기
file_list = os.listdir(upper_path)
file_count = len(file_list)

rope = 0
# find_image_url 함수 실행
for file in os.listdir(upper_path):
    rope += 1
    if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):  # 이미지 파일만 처리
        print(file_count, "중", rope, "항목 처리 중")
        find_image_url(upper_path + "\\" + file, rope)

# 데이터프레임 생성 및 저장
driver.quit()

df = pd.DataFrame({'파일명': filename_list, '구글 검색 url': url_list, '유사도': similarity_list, '유사 이미지 링크': searched_url_list, '찍은 날짜': taken_date_list, '만든 날짜': created_date_list, '수정한 날짜': modified_date_list, '프로그램 이름': program_name_list})
while True:
    try:
        df.to_excel(f"C:\\Users\\{user}\\Desktop\\img_links.xlsx", index=False)
        print("엑셀 파일이 성공적으로 저장되었습니다.")
        break  # 성공적으로 저장되었으므로 반복문 종료
    except Exception as e:
        print(f"엑셀 파일 저장 중 오류가 발생했습니다: {e}")
        print("img_links.xlsx 엑셀 파일이 열려있는 경우 종료해주시고 엔터하면 저장을 재시도합니다")
        a = input()
        continue  # 예외가 발생하면 다시 시도
print("바탕화면에 img_links.xlsx 이름으로 저장되었습니다")
print("엔터를 누르면 프로그램이 종료됩니다")

a = input()
