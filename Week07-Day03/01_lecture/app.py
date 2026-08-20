import streamlit as st

st.set_page_config(page_title="EXAONE Chat")
st.title("EXAONE 로컬 챗봇")

prompt = st.chat_input("질문을 입력하세요")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        st.write(f"입력한 질문: {prompt}")
