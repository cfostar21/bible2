import streamlit as st


st.set_page_config(page_title="main", page_icon="🐕")
st.write("# Welcom to Pov Predction App")
st.markdown(
    """
    과산화물가를 예측하기 위한 Application입니다.
    페이지는 2개로 나누어져있습니다.
    1. predction - 훈련된 모델을 이용해 TPM 수치치를 예측하는 페이지 입니다.
    2. training - 수집된 데이터를 이용해 회귀 모델을 훈련하는 페이지 입니다.
    3. data - 수집된 데이터를 조회하는 페이지 입니다.
    """
)
