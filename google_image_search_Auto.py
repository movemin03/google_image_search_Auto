import os
import numpy as np
from PIL import Image
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pywinauto.application import Application
import io
import base64
import cv2
from skimage.metrics import structural_similarity as ssim

source_dir = input("사진이 들어있는 폴더 경로를 넣어주세요(put your folder path):").replace("'", "").replace('"', "")
dest_dir = source_dir + "\\converted"

def chk_dest_dir(dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        # 대상 디렉토리가 비어있지 않다면
        if os.listdir(dest_dir):
            # 사용자에게 삭제 여부를 물어봅니다.
            answer = input("폴더가 비어있지 않습니다. 모든 항목을 삭제하시겠습니까? (y/n): ")
            if answer.lower() == 'y':
                # 'y'라고 답하면 폴더 안의 모든 항목을 삭제합니다.
                shutil.rmtree(dest_dir)
                os.makedirs(dest_dir)
chk_dest_dir(dest_dir)

# 파일 용량 체크
def check_size(file):
    return os.path.getsize(file)

# 이미지 압축
def compress_image(image_path, output_folder, desired_size, idx):
    img = Image.open(image_path)
    img.save(f"{output_folder}\\{idx}.jpg", quality=90, optimize=True)

index_table = []


# 파일 처리
def process_files(source_dir, dest_dir):
    print("처리를 시작합니다. 별도의 안내가 있을 때까지 종료하지 마십시오")
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
print("이미지 전처리 중입니다\n이미지가 많을 시 처리에 시간이 걸릴 수 있습니다")
process_files(source_dir, dest_dir)
print(dest_dir + "폴더에 저장되었습니다.")

user = os.getlogin()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\Users\\' + user + r'\\AppData\\Local\\Google\\Chrome\\User Data"')
option = Options()
option.add_argument(f"user-agent={user_agent}")
option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=option)

driver.get("https://images.google.com/")

# 리스트 초기화
filename_list = []
url_list = []
similarity_list = []



def calculate_ssim(image1, image2):
    # 이미지를 그레이스케일로 변환
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 유사도 계산
    (_, similarity) = ssim(gray1, gray2, full=True)
    return similarity


def base64_to_image(base64_string):
    # base64 문자열을 이미지로 디코딩
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def image_similarity(base64_string, path):
    # base64 이미지를 이미지로 변환
    base64_image = base64_to_image(base64_string)
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
def find_image_url(path):
    print("처리 중")
    driver.get("https://images.google.com/")
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]"))
    )
    element.click()

    time.sleep(1)
    img_upload_xpath = '//span[contains(text(), "파일을 업로드")]'
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, img_upload_xpath))
    )
    element.click()

    # 이름이 '열기'인 창이 나올 때까지 3초간 대기
    time.sleep(1)
    app = Application().connect(title_re="열기")
    app["열기"].Edit1.set_text(path)
    app["열기"].Button1.click()

    # URL 갱신 확인 후 저장
    time.sleep(2)  # 페이지 로딩 대기
    new_url = driver.current_url
    url_list.append(new_url)

    filename_list.append(get_value_by_index(index_table, int(os.path.splitext(os.path.basename(path))[0])))
    print("검색 url 저장 완료")
    time.sleep(1)

    while True:
        try:
            searched_img = driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/div/div[1]/div/div[2]/div/img')
            break
        except:
            # 요소를 찾지 못한 경우, 예외 처리 후 다시 시도
            print("이미지 업로드를 제대로 완료한 후 엔터")
            a = input()
            continue
    searched_img = driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/div/div[1]/div/div[2]/div/img')
    base64_string = searched_img.get_attribute("src")
    base64_string = base64_string.split(',')[1]
    if base64_string:
        similarity = image_similarity(base64_string, path) * 100
        print("유사도:", similarity)
    else:
        similarity = 0
        print("유사도를 검색할 수 없습니다")
    similarity_list.append(similarity)

upper_path = dest_dir

# 폴더 내 모든 파일에 대해 반복
for file in os.listdir(upper_path):
    if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):  # 이미지 파일만 처리
        # 함수 호출
        find_image_url(upper_path + "\\" + file)

# 데이터프레임 생성 및 저장
df = pd.DataFrame({'filename': filename_list, 'url': url_list, '유사도': similarity_list})
while True:
    try:
        df.to_excel(f"C:\\Users\\{user}\\Desktop\\img_links.xlsx", index=False)
        print("엑셀 파일이 성공적으로 저장되었습니다.")
        break  # 성공적으로 저장되었으므로 반복문 종료
    except Exception as e:
        print(f"엑셀 파일 저장 중 오류가 발생했습니다: {e}")
        print("파일이 열려있는 경우 종료해주시고 엔터")
        a = input()
        continue  # 예외가 발생하면 다시 시도
print("바탕화면에 img_links.xlsx 이름으로 저장되었습니다")
# 웹드라이버 종료
driver.quit()
a = input()
