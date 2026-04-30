import streamlit as st
import pandas as pd
from difflib import get_close_matches
import cv2
import numpy as np

# 1. 엑셀 리스트 로드 (제품리스트.xlsx)
@st.cache_data
def load_master_list():
    df = pd.read_excel('제품리스트.xlsx', header=None)
    # 첫 번째 열(A열) 데이터를 리스트로 변환
    return df[0].astype(str).tolist()

master_list = load_master_list()

st.title("🛡️ 신원화학 품질관리 스캔 시스템")
st.write(f"현재 등록된 제품 수: {len(master_list)}개")

# 2. 스마트폰 카메라 입력
img_file = st.camera_input("스티로폼 박스의 QR 코드를 찍어주세요")

if img_file:
    # 이미지 처리 (QR 인식 준비)
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    opencv_img = cv2.imdecode(file_bytes, 1)
    
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(opencv_img)

    if data:
        st.subheader("🔍 스캔 결과")
        
        # 3. 지능형 매칭 (유사도 검사)
        # n=1: 가장 비슷한 것 1개, cutoff=0.6: 60% 이상 일치 시 보정
        match = get_close_matches(data, master_list, n=1, cutoff=0.6)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"인식된 원본값\n\n**{data}**")
        
        with col2:
            if match:
                st.success(f"최종 교정 결과\n\n**{match[0]}**")
                st.balloons() # 매칭 성공 시 축하 효과
            else:
                st.warning("유사 제품 없음")
                st.write("리스트에 없는 제품이거나 오염이 심합니다.")
                
    else:
        st.error("QR 코드를 찾을 수 없습니다. 조명을 조절하거나 더 가까이 찍어주세요.")

# 4. 설정 기억 (간단한 로그 출력)
if st.checkbox("최근 검사 이력 보기"):
    st.write("마지막 작업 폴더: `C:/Quality_Logs/2026-04/` (예시)")
