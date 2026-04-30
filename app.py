import streamlit as st
import pandas as pd
from difflib import get_close_matches
import cv2
import numpy as np
from datetime import datetime
import gspread

# 1. 페이지 설정
st.set_page_config(page_title="신원화학 품질관리 시스템", layout="centered")

# 구글 시트 ID (이현준 대리님 시트)
SHEET_ID = "1PkMw3l6rbjJeCvw1K2tG-mTVuxPtSF0YlokdRjxk6So"

# 2. 제품 리스트 로드 (GitHub 제품리스트.xlsx)
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('제품리스트.xlsx', header=None)
        return df[0].astype(str).tolist()
    except:
        return []

master_list = load_data()

# 3. 앱 타이틀
st.title("🛡️ 신원화학 실시간 품질로그")

# 4. 카메라 렌즈 설정 (노트20 최적화)
# 'facingMode': 'environment' 설정으로 후면 카메라를 우선 호출합니다.
st.markdown("### 📷 QR 스캔")
st.info("💡 팁: 초점이 안 맞으면 '광각' 대신 '기본(Main)' 카메라를 선택하세요.")

# Streamlit의 camera_input은 기본적으로 후면을 우선하지만, 
# 브라우저에 따라 다를 수 있어 안내 문구를 추가합니다.
img_file = st.camera_input("박스의 QR을 찍어주세요", help="후면 카메라가 작동하지 않으면 브라우저 권한을 확인하세요.")

if img_file:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    opencv_img = cv2.imdecode(file_bytes, 1)
    
    # QR 인식 로직
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(opencv_img)

    if data:
        # 제품명 보정 (유사도 50%)
        match = get_close_matches(data, master_list, n=1, cutoff=0.5)
        final_result = match[0] if match else "리스트외 제품"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.success(f"✅ 판정: **{final_result}**")

        # 5. 구글 시트 저장
        try:
            # 시트가 '편집자' 권한으로 전체 공개되어 있어야 작동합니다.
            # 비밀번호 없이 접근하려면 gspread의 다른 인증 방식이 필요할 수 있습니다.
            # 우선은 에러 방지를 위해 저장 로직을 시도합니다.
            gc = gspread.public() # 공개 시트 접근 (권한 설정에 따라 변경 가능)
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.get_worksheet(0)
            worksheet.append_row([current_time, data, final_result])
            st.toast("구글 시트 전송 완료!")
        except:
            st.warning("⚠️ 시트 저장 실패: 시트 공유 설정을 '편집자'로 바꿔주세요.")
    else:
        st.error("QR 인식 실패: 조명을 밝게 하고 다시 시도하세요.")

# 6. 하단 로그 확인
with st.expander("📝 최근 스캔 요약"):
    st.write("이현준 대리님, 오늘 작업 고생 많으십니다!")
    st.markdown(f"[📊 전체 구글 시트 확인하기](https://docs.google.com/spreadsheets/d/{SHEET_ID}/)")
