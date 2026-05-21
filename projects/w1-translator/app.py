import streamlit as st
import pandas as pd
from translator import translate

st.set_page_config(page_title="翻译工具", page_icon="🌏")
if "history" not in st.session_state:
      st.session_state.history = []
      st.session_state.last_result = ""  # 加这行
st.sidebar.title("设置")
target_langs = st.sidebar.multiselect("目标语言", ["日文", "英文", "韩文", "法文"], default=["日文"])
st.sidebar.write("---")
extra_features = st.sidebar.multiselect("额外功能", ["显示原文", "显示音标", "保存到历史"])
st.sidebar.write(f"已选：{extra_features}")
st.title("🌏 中文 → " + " → ".join(target_langs) + "翻译")
# ── Tab 1：单条翻译 ──
tab1, tab2 = st.tabs(["单条翻译", "批量翻译"])

with tab1:
      col1, col2 = st.columns(2)
      with col1:
          text = st.text_area("输入要翻译的中文：", height=150, key="single")
          if st.button("翻译", type="primary"):
              if not text.strip():
                  st.warning("请输入文字。")
              else:
                  all_results = {}
                  for lang in target_langs:
                    with st.spinner(f"翻译成{lang}..."):
                      all_results[lang] = translate(text, lang)
              st.session_state.last_result = all_results
              for lang, result in all_results.items():
                  st.session_state.history.append((text, result, lang))
      with col2:
          last = st.session_state.get("last_result", {})
          display_text = ""
          if last:
            display_text = "\n".join([f"{lang}: {result}" for lang, result in last.items()])
          st.text_area("译文", value=display_text, height=150)
  # ── Tab 2：批量翻译 ──
with tab2:
      uploaded = st.file_uploader("上传一个文本文件（每行一条中文）", type=["txt"])
      if uploaded is not None:
          content = uploaded.getvalue().decode("utf-8")
          lines = [line.rstrip("\n") for line in content.splitlines() if line.strip()]
          st.info(f"共检测到 {len(lines)} 条待翻译文本")

          if st.button("开始批量翻译", type="primary"):
              progress_bar = st.progress(0, text="准备中...")
              results = []
              for i, line in enumerate(lines):
                  progress_bar.progress((i + 1) / len(lines), text=f"翻译第 {i+1}/{len(lines)} 条")
                  result = translate(line, target_langs)
                  results.append(f"{line} -> {result}")

              st.success("批量翻译完成！")
              for line, r in zip(lines, results):
                 st.session_state.history.append((line, r, target_langs))
              df = pd.DataFrame({"原文": lines, "译文": [r.split(" -> ")[1] for r in results]})
              st.dataframe(df, use_container_width=True)
              #下载结果 
              st.download_button("下载结果", data="\n".join(results), file_name="translation_results.txt")
   
    # ── expender：翻译历史 ──
with st.expander(f"📋 翻译历史（{len(st.session_state.history)} 条）"):
      if not st.session_state.history:
          st.info("还没有翻译记录。")
      else:
          for i, (src, tgt, lang) in enumerate(st.session_state.history, 1):
              st.write(f"{i}. [{lang}] {src} → {tgt}")            