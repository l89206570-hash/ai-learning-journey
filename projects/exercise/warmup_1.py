#写一个计数器页面：点击 +1 → session_state 存 → st.rerun()
import streamlit as st

# ❌ 问题1：st.button("+1") 返回的是布尔值（True/False），不是用来判断状态是否存在的。
#    应该用 if "count" not in st.session_state:
if st.button("+1") not in st.session_state:
    st.session_state["+1"] = 0

# ❌ 问题2：两个按钮用了相同的 label "+1"，Streamlit 会混淆，导致行为异常
# ❌ 问题3：key 命名为 "+1" 含义不清，建议用 "count"
# ❌ 问题4：没有写 st.write() 或 st.title() 来展示计数，用户看不到数字
if st.button("+1"):
    st.session_state["+1"] = st.session_state["+1"] + 1
    st.write()
    st.rerun()


if "count" not in st.session_state:
    st.session_state["count"] = 0

if st.button("+1"):
    st.session_state["count"] = st.session_state["count"] + 1
    st.write(st.session_state["count"])
    st.rerun()

