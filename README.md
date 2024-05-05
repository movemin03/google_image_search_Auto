# Google Image Search Auto(영어 설명)

Google Image Search Auto is an innovative program designed to search for similar images within a local folder using Google's image search functionality and compare their similarity.

## Key Features:
- **Google Image Search Integration:** Utilizes web scraping techniques to directly crawl Google's image website for efficient image retrieval.
- **Two Operation Modes:**
  - **google_image_search_Auto.py:** Operates by directly crawling Google's image website. Requires the installation of the "Chrome browser".
  - **google_image_search_Auto_GoogleVisionAPI_ver.py:** Utilizes Google Vision API for image search. Requires prior setup for Google Vision usage on your local machine.
- **SSIM Model for Similarity Verification:** Employs the SSIM (Structural Similarity Index) model to measure image similarity.
- **Flexible Plagiarism Threshold:** Customize the plagiarism threshold according to your needs. Conservative threshold: 70 or above; broader threshold: 50 or above.

## Usage:
1. **Clone Repository:** Clone the repository to your local machine.
2. **Install Dependencies:** Ensure all necessary dependencies are installed.
3. **Run the Script:** Execute the desired script based on your preference.
   ```python
   python google_image_search_Auto.py
   ```
   or
   ```python
   python google_image_search_Auto_GoogleVisionAPI_ver.py
   ```

## **Exporting as Executable:**
To export the program as an executable (.exe) file using PyInstaller, use the following command as an example:

```cmd
pyinstaller C:\Users\USER_NAME\Desktop\google_image_search_Auto.py --onefile --hidden-import os --hidden-import time --hidden-import datetime --hidden-import urllib.request --hidden-import shutil --hidden-import pandas --hidden-import numpy --hidden-import requests --hidden-import pillow --hidden-import selenium --hidden-import io --hidden-import scikit-image --hidden-import PIL.ExifTags --hidden-import multiprocessing --hidden-import opencv-python
```

For detailed information on setting up Google Vision API, refer to the official documentation [here](https://cloud.google.com/vision/docs/detecting-web?hl=ko).

Google Image Search Auto offers a seamless solution for image similarity comparison, empowering users with efficient and accurate results. 
Dive into the world of image analysis with Google Image Search Auto today! 📸✨


------
# Google Image Search Auto (한국어 설명)

구글 이미지 검색 자동화는 구글의 이미지 검색 기능을 활용하여 로컬 폴더 내에서 유사한 이미지를 검색하고 그 유사성을 비교하는 혁신적인 프로그램입니다.

## 주요 기능:
- **구글 이미지 검색 통합:** 웹 스크래핑 기술을 사용하여 구글의 이미지 웹사이트를 직접 크롤링하여 이미지를 효율적으로 검색합니다.
- **두 가지 작동 모드:**
  - **google_image_search_Auto.py:** 구글의 이미지 웹사이트를 직접 크롤링하여 작동합니다. "크롬 브라우저"의 설치가 필요합니다.
  - **google_image_search_Auto_GoogleVisionAPI_ver.py:** Google Vision API를 활용하여 이미지 검색을 수행합니다. 로컬 환경에서 Google Vision 사용을 위한 사전 설정이 필요합니다.
- **SSIM 모델을 활용한 유사성 검증:** SSIM (Structural Similarity Index) 모델을 사용하여 이미지 유사성을 측정합니다.
- **유연한 표절 임계값:** 사용자의 요구에 따라 표절 임계값을 조정할 수 있습니다. 보수적인 임계값: 70 이상; 넓은 임계값: 50 이상.

## 사용 방법:
1. **저장소 복제:** 저장소를 로컬 머신으로 복제합니다.
2. **의존성 설치:** 필요한 모든 종속성이 설치되어 있는지 확인합니다.
3. **스크립트 실행:** 원하는 스크립트를 실행합니다.
   ```python
   python google_image_search_Auto.py
   ```
   또는
      ```python
   python google_image_search_Auto_GoogleVisionAPI_ver.py
   ```
## 실행 파일로 내보내기:
PyInstaller를 사용하여 프로그램을 실행 파일(.exe)로 내보내려면 다음 명령을 사용합니다.
```cmd
pyinstaller C:\Users\USER_NAME\Desktop\google_image_search_Auto.py --onefile --hidden-import os --hidden-import time --hidden-import datetime --hidden-import urllib.request --hidden-import shutil --hidden-import pandas --hidden-import numpy --hidden-import requests --hidden-import pillow --hidden-import selenium --hidden-import io --hidden-import scikit-image --hidden-import PIL.ExifTags --hidden-import multiprocessing --hidden-import opencv-python
```
Google Vision API 설정에 대한 자세한 내용은 [여기](https://cloud.google.com/vision/docs/detecting-web?hl=ko)를 참조하십시오.

구글 이미지 검색 자동화는 사용자에게 효율적이고 정확한 결과를 제공하여 이미지 유사성 비교를 원활하게 도와줍니다. 
지금 바로 구글 이미지 검색 자동화로 이미지 분석의 세계로 뛰어들어보세요! 📸✨


   
