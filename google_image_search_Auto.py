import os
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

source_dir = input("사진이 들어있는 폴더 경로를 넣어주세요(put your folder path):").replace("'", "").replace('"', "")
dest_dir = source_dir + "\사진변환"

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
def compress_image(image_path, output_folder, desired_size):
    img = Image.open(image_path)
    img.save(f"{output_folder}\\{os.path.basename(image_path)}", quality=90, optimize=True)

# 파일 처리
def process_files(source_folder, dest_folder):
    print("처리를 시작합니다. 별도의 안내가 있을 때까지 종료하지 마십시오")
    for foldername, subfolders, filenames in os.walk(source_folder):
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'): # 이미지 파일인 경우
                file_path = os.path.join(foldername, filename)
                compress_image(file_path, dest_folder, 195) # 이미지 압축

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
filename = []
url = []

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
    url.append(new_url)
    filename.append(os.path.basename(path))
    print("처리 완료")

upper_path = dest_dir

# 폴더 내 모든 파일에 대해 반복
for file in os.listdir(upper_path):
    if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):  # 이미지 파일만 처리
        # 함수 호출
        find_image_url(upper_path + "\\" + file)

# 데이터프레임 생성 및 저장
df = pd.DataFrame({'filename': filename, 'url': url})
df.to_excel("C:\\Users\\" + user + "\\Desktop\\img_links.xlsx", index=False)
print("바탕화면에 img_links.xlsx 이름으로 저장되었습니다")
# 웹드라이버 종료
driver.quit()
a = input()
