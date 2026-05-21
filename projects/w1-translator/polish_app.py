 # practice.py — 邮件润色函数
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
      api_key=os.getenv("DEEPSEEK_API_KEY"),
      base_url="https://api.deepseek.com",
  )

def polish(draft: str, style: str) -> str:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是一个专业的邮件润色助手，帮我把下面的邮件草稿润色成{style}风格。"},
                {"role": "user", "content": draft}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"润色过程中出现错误: {e}")
        return "润色失败，请重试。"

#要求：1. 页面标题"邮件润色助手"
st.set_page_config(page_title="邮件润色助手", page_icon="✉️")
if "polish_history" not in st.session_state:
      st.session_state.polish_history = []
st.title("✉️ 邮件润色助手")
#  2. 一个多行输入框贴草稿
text = st.text_area("请输入邮件草稿：", height=200) 
# 3. 一个下拉框选风格（正式/友好/简洁） 
style = st.selectbox("请选择润色风格：", options=["正式", "友好", "简洁"])
# 4. 一个"润色"按钮 
if st.button("润色", type="primary"):
      if not text.strip():
          st.warning("请输入邮件草稿。")
      else:
          with st.spinner("正在润色..."):
              result = polish(text, style)
          st.success("润色完成！")
          st.session_state.polish_history.append((text, result, style))
          st.text_area("润色结果：", value=result, height=200)
st.sidebar.write("---")
st.sidebar.subheader("润色历史")
if not st.session_state.polish_history:
      st.sidebar.info("暂无记录")
else:
      for i, (src, res, sty) in enumerate(st.session_state.polish_history[-5:], 1):
          with st.sidebar.expander(f"#{i} [{sty}]"):
              st.sidebar.write(f"**原文:** {src[:50]}..." if len(src) > 50 else f"**原文:** {src}")
              st.sidebar.write(f"**结果:** {res[:50]}..." if len(res) > 50 else f"**结果:** {res}")
# 5. 点按钮后调 polish()，结果显示在页面上
