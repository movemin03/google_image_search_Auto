google_image_search_Auto

본 프로그램은 로컬 폴더 내 이미지를 구글의 이미지로 검색 기능을 활용하여 유사 이미지를 검색 후 유사도를 비교하는 프로그램입니다.
google_image_search_Auto.py 의 경우, 구글 이미지 웹사이트를 직접 크롤링하는 방식으로 작동하며 "크롬 브라우저" 가 설치되어 있어야 합니다.
google_image_search_Auto_GoogleVisionAPI_ver.py 의 경우, 구글 비전 api 를 활용한 방식으로 로컬 컴퓨터에 Google Vision 사용을 위한 사전 작업이 완료되어있어야 합니다.
구글 비전 api 를 활용하기 위한 자세한 내용은 https://cloud.google.com/vision/docs/detecting-web? 공식 문서를 참조해주십시오.

유사도 검증은 SSIM 모델을 사용하고 있습니다.

아래는 pyinstaller 를 통해 exe 파일로 내보내기 위한 명령어 예시입니다.
pyinstaller C:\Users\USER_NAME\Desktop\google_image_search_Auto.py --onefile --hidden-import os --hidden-import time --hidden-import datetime --hidden-import urllib.request --hidden-import shutil --hidden-import pandas --hidden-import numpy --hidden-import requests --hidden-import pillow --hidden-import selenium --hidden-import io --hidden-import scikit-image --hidden-import PIL.ExifTags --hidden-import multiprocessing --hidden-import opencv-python

