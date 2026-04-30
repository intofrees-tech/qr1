import streamlit as st
import pandas as pd
from difflib import get_close_matches
import cv2
import numpy as np
from datetime import datetime
import gspread
from src.google_auth import get_gspread_client # 보안 설정을 위해 필요 (아래 설명 참조)

# 1. 페이지 설정 및 시트 연결
st.set_page_config(page_title="신원화학 실시간 로그", page_icon="📊")

# 구글 시트 연결 (공개 시트일 경우 간편 설정)
SHEET_ID = "1PkMw3l6rbjJeCvw1K2tG-mTVuxPtSF0YlokdRjxk6So"

# 2. 제품 리스트 로드
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

# 3. 카메라 입력
img_file = st.camera_input("QR 스캔")

if img_file:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    opencv_img = cv2.imdecode(file_bytes, 1)
    
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(opencv_img)

    if data:
        # 유사도 보정
        match = get_close_matches(data, master_list, n=1, cutoff=0.5)
        final_result = match[0] if match else "리스트외 제품"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.success(f"**판정 결과: {final_result}**")

        # 4. 구글 시트에 한 줄 추가 (Append)
        try:
            # Streamlit Cloud의 Secrets에 저장된 자격증명으로 로그인
            gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.get_worksheet(0) # 첫 번째 시트 선택
            
            # [시간, 인식값, 최종판정] 순서로 한 줄 추가
            worksheet.append_row([current_time, data, final_result])
            st.toast("✅ 구글 시트 저장 완료!")
        except Exception as e:
            st.error(f"시트 저장 실패 (권한 설정 확인 필요): {e}")
    else:
        st.error("QR 인식 실패")

# 5. 설정 및 가이드 (노트20)
st.sidebar.header("⚙️ 환경 설정")
st.sidebar.write(f"담당자: 이현준 대리")
st.sidebar.markdown(f"[📊 구글 시트 열기](https://docs.google.com/spreadsheets/d/{SHEET_ID}/)")
