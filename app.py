import streamlit as st
import pandas as pd
from difflib import get_close_matches
import cv2
import numpy as np
from datetime import datetime
import gspread

# 1. 페이지 및 시트 설정
st.set_page_config(page_title="신원화학 실시간 로그", page_icon="📊")

# 대리님이 주신 구글 시트 ID
SHEET_ID = "1PkMw3l6rbjJeCvw1K2tG-mTVuxPtSF0YlokdRjxk6So"

# 2. 제품 리스트 로드 (GitHub에 올린 제품리스트.xlsx 참조)
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('제품리스트.xlsx', header=None)
        return df[0].astype(str).tolist()
    except:
        return []

master_list = load_data()

st.title("🛡️ 실시간 품질관리 시스템")
st.info("촬영 즉시 구글 시트에 기록됩니다.")

# 3. 카메라 입력 (노트20 최적화)
img_file = st.camera_input("QR 스캔")

if img_file:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    opencv_img = cv2.imdecode(file_bytes, 1)
    
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(opencv_img)

    if data:
        # 제품명 보정 (엑셀 리스트 대조)
        match = get_close_matches(data, master_list, n=1, cutoff=0.5)
        final_result = match[0] if match else "리스트외 제품"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.success(f"**판정 결과: {final_result}**")

        # 4. 구글 시트에 데이터 쓰기
        try:
            # 주소창의 링크만으로 접근하는 방식 (비밀번호/키 파일 없이 시트가 공개 편집 상태여야 함)
            # 주의: Streamlit Cloud Secrets에 구글 인증 정보가 없다면 아래 방식이 가장 빠릅니다.
            gc = gspread.oauth() # 혹은 서비스 계정 설정 필요
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.get_worksheet(0)
            
            worksheet.append_row([current_time, data, final_result])
            st.toast("✅ 구글 시트 저장 완료!")
        except Exception as e:
            # 인증 설정이 안 되어 있을 때 안내
            st.error("구글 시트 접근 권한이 필요합니다.")
            st.info("💡 팁: 시트의 [공유] 버튼을 눌러 '편집자' 권한을 주셨는지 확인해 주세요.")
    else:
        st.error("QR 인식 실패")

# 사이드바 설정
st.sidebar.write(f"담당자: 이현준 대리")
st.sidebar.markdown(f"[📊 구글 시트 바로가기](https://docs.google.com/spreadsheets/d/{SHEET_ID}/)")
