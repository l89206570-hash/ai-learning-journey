# W2 Day 1 — 多模型对比器
import streamlit as st
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = {
    "deepseek": OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    ),
    "qwen": OpenAI(
        api_key=os.getenv("QWEN_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
    "mimo": OpenAI(
        api_key=os.getenv("MIMO_API_KEY"),
        base_url="https://token-plan-cn.xiaomimimo.com/v1",
    )
}

MODELS = {
    "deepseek-v4-flash": {
        "name": "DS V4 Flash",
        "model": "deepseek-v4-flash",
        "description": "V4 轻量版，快速省钱（原 deepseek-chat）",
        "icon": "⚡",
        "provider": "deepseek",
    },
    "deepseek-v4-flash-reasoning": {
        "name": "DS V4 Flash (思考)",
        "model": "deepseek-v4-flash",
        "description": "V4 思考模式，复杂推理（原 deepseek-reasoner）",
        "icon": "⚡🧠",
        "provider": "deepseek",
    },
    "deepseek-v4-pro": {
        "name": "DS V4 Pro",
        "model": "deepseek-v4-pro",
        "description": "V4 旗舰版，强推理+好中文",
        "icon": "🔥",
        "provider": "deepseek",
    },
    "qwen": {
        "name": "Qwen",
        "model": "qwen-plus",
        "description": "通义千问，全能助手",
        "icon": "�",
        "provider": "qwen",
    },
    "mimo": {
        "name": "mimo",
        "model": "mimo-v2.5-pro",
        "description": "多模态推理，详细解释",
        "icon": "🧠",
        "provider": "mimo",
    },
}


def call_model(model_config: dict, prompt: str, system_prompt: str = "") -> dict:
    try:
        start = time.time()
        response = client[model_config["provider"]].chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        choice = response.choices[0]
        elapsed = time.time() - start
        return {
            "success": True,
            "content": choice.message.content.strip(),
            "reasoning": getattr(choice.message, "reasoning_content", None),
            "time_seconds": elapsed,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "time_seconds": time.time() - start}


# ═══════════════════════════════════════
# Streamlit UI
# ═══════════════════════════════════════

st.set_page_config(page_title="模型对比器", page_icon="🤖")

# —— session_state 初始化（只在第一次运行时执行）——
if "battle_history" not in st.session_state:
    st.session_state.battle_history = []
if "last_battle" not in st.session_state:
    st.session_state.last_battle = None

# —— sidebar：模型选择 ——
st.sidebar.title("模型选择")
selected_models = {}
for key, config in MODELS.items():
    if st.sidebar.checkbox(config["name"], value=True, help=config["description"]):
        selected_models[key] = config

# —— 主区域：输入 ——
text = st.text_area("请输入问题", height=150)

if st.button("开始对比", type="primary"):
    if not text.strip():
        st.warning("请输入一个问题进行对比。")
    else:
        with st.spinner("正在调用模型..."):
            results = {}
            for key, config in selected_models.items():
                with st.spinner(f"等待 {config['name']}..."):
                    results[key] = call_model(config, text)

            # ① 存完整结果 — 给展示区用（页面下方并排卡片）
            st.session_state.last_battle = {
                "prompt": text,
                "results": results,
                "models": list(selected_models.keys()),
            }
            # ② 存精简版到历史 — 给 sidebar 历史列表用（每条约 200 字，省内存）
            st.session_state.battle_history.append({
                "prompt": text,
                "results": {k: {
                    "success": v["success"],
                    "content": v.get("content", "")[:200],  # 截断到 200 字
                    "time_seconds": v.get("time_seconds"),
                    "total_tokens": v.get("total_tokens"),
                } for k, v in results.items()},
                "models": list(selected_models.keys()),
            })
            # ③ 手动刷新页面 — 让按钮复位，让展示区从 session_state 读取新数据
            st.rerun()

# ═══ 以下全部在按钮外面，每次重跑都重新渲染 ═══

# —— sidebar：对比历史（★ 今天新增 — reversed() 倒序 + 列表切片 [::-1]）——
with st.sidebar.expander(f"📋 对比历史（{len(st.session_state.battle_history)} 条）"):
    if not st.session_state.battle_history:
        st.info("还没有对比记录")
    else:
        # [::-1] 倒序遍历：最新记录排在最上面，编号 #1
        for i, record in enumerate(st.session_state.battle_history[::-1], 1):
            st.caption(f"#{i}: {record['prompt'][:30]}")  # 只显示前 30 字
            first_key = record['models'][0]
            preview = record['results'][first_key].get('content', '')[:50]
            st.caption(f"   {preview}...")  # 显示第一个模型的前 50 字结果预览
            st.divider()

# —— 主区域：展示上次对比结果 ——
if st.session_state.last_battle:
    last = st.session_state.last_battle
    st.divider()
    st.subheader("对比结果")
    st.caption(f"Prompt: {last['prompt'][:100]}")
    model_keys = list(last["results"].keys())
    cols = st.columns(len(model_keys))
    for i, key in enumerate(model_keys):
        config = MODELS[key]
        result = last["results"][key]
        with cols[i]:
            st.subheader(f"{config['icon']} {config['name']}")
            if result["success"]:
                st.write(result["content"])
                st.caption(f"耗时: {result['time_seconds']:.2f}s | Tokens: {result['total_tokens']}")
            else:
                st.error(f"调用失败: {result.get('error', '')}")
