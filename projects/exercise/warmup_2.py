#标签页切换器：3 个 tab 切换时重建不同 chat_engine

import streamlit as st

MODELS ={
name : "deepseek-chat",
model : "deepseek-v4-flash",
"",


name : "deepseek-reasoning",
model : "deepseek-v4-pro",
"",



name : "qwen",
model : "qwen-",



}    

st.title("标签页切换器")
st.sidebar.subheader("模型选择")

st.divider

st.selectbox = (MDOELS, option, key="name"),

