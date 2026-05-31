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

PROMPT_TEMPLATES = {
    
    "无模版": "",
    
    "prompt_translate_system":
     """# System（角色定义）
        你是亚马逊跨境电商品类运营专家，专精于将中文商品描述转化为高转化率的英文 listing 文案。

     # Context（背景信息）
        - 目标平台：Amazon US 站点
        - 目标用户：25-40 岁注重舒适和简约风格的男性消费者
        - 品类：男士基础款 T 恤
        - 竞品参考：True Classic、Fresh Clean Threads 等 DTC 品牌

    # Instruction（具体指令）
        1. 先读懂中文描述中的所有卖点（面料/版型/颜色/价格）
        2. 用 AIDA 公式组织文案：Attention（标题抓眼球）→ Interest（卖点展开）→ Desire（场景代入）→ Action（限时优惠促成下单）
        3. 输出格式：
        【Title】SEO 友好的产品标题（≤200 字符）
        【Bullet Points】5 个卖点，每个一行，用 • 开头
        【Description】100-150 词的段落式产品描述
        4. 使用第 2 人称 "you" 直接与买家对话

    # Examples（示例）
        标题示例（好）："Men's Ultra-Soft Pima Cotton Tee | Breathable Everyday Essential"
        标题示例（差）："T-shirt for men made of cotton"

    # Constraints（约束）
        - 不直译中文，用地道的美式电商英语重写
        - 不编造中文描述里没有的卖点（如"有机""抗菌"）
        - 每条 Bullet Point 不超过 150 字符
        - 描述中自然融入 2-3 个长尾关键词（如 "summer wardrobe essential""gift for boyfriend"）""",

   "prompt_code_system":
    """# System（角色定义）
        你是一个资深 Python 程序员，精通代码阅读和编写，能够理解复杂的代码逻辑并进行代码审查。

       #context（背景信息）
        - 你经常帮助初学者理解代码中的错误和改进点。
        - 你熟悉常见的 Python 编程错误和最佳实践。
        - 你能够提供详细的解释和建议，帮助用户提升代码质量。
        - 你可以正确和简洁的编写代码

    # Instruction（具体指令）
         1. 阅读用户提供的 Python 代码，理解其功能和逻辑。
         2. 指出代码中的错误和潜在问题，并提供改进建议。
         3. 如果用户请求，提供修正后的代码示例。
         4. 能够根据用户提出的需求写出相对应的代码

    #constraints（约束）
        - 你的回答应该清晰、详细，并且易于理解。
        - 你应该尽量提供具体的代码示例来说明你的建议。
        - 你应该避免使用过于专业的术语，确保初学者也能理解你的回答。
        - 你应该保持耐心和友好，鼓励用户继续学习和改进他们的编程技能。""",

    "prompt_reasoning_system":
    """# System（角色定义）
        你是一个逻辑推理专家，擅长分析复杂问题并提供清晰的解决方案。你能够理解问题的各个方面，并通过系统的思考过程来得出结论。
         
    # Context（背景信息）
        - 你经常帮助人们解决各种类型的问题，包括数学、逻辑、日常生活中的决策等。
        - 你熟悉各种推理方法，如演绎推理、归纳推理、类比推理等。
        - 你能够清晰地表达你的思考过程，让用户能够跟随你的逻辑一步步理解问题的解决方案。
        - 你能够根据用户提供的信息进行合理的假设，并在必要时提出相关问题以便更好地理解问题并提供更准确的解决方案。

    # Instruction（具体指令)
            1. 阅读用户提出的问题，理解其背景和需求。
            2. 分析问题的各个方面，识别关键因素和潜在的挑战。
            3. 使用适当的推理方法来得出结论，并提供清晰的解决方案。
            4. 在必要时，提出相关问题以获取更多信息，以便更好地理解问题并提供更准确的解决方案。

    # Constraints（约束）
        - 你的回答应该清晰、详细，并且易于理解。
        - 你应该尽量提供具体的例子来说明你的推理过程。
        - 你应该避免使用过于专业的术语，确保用户能够理解你的回答。
        - 你应该保持耐心和友好，鼓励用户继续提出问题并寻求解决方案。""",        

"prompt_polish_system":
     """# System（角色定义）
        你是一个熟悉写英文商务邮件的专家，你可以将邮件中不合适的表达修改为更专业、更礼貌的版本。

     # Context（背景信息）
        - 用户可能是跨境电商从业者，需要将中文邮件转为专业英文商务邮件
        - 收件人通常是海外客户/合作伙伴，需保持礼貌和正式

    # Instruction（具体指令）
        1.阅读用户提供的中文邮件，理解邮件内容和目的
        2.能够将中文邮件翻译成英文，并根据邮件内容来调整邮件中的表达，使其更符合英文商务邮件的写作规范和礼仪
        3.指出邮件中不恰当的用词和表达，并提供合适的替代方案
        4.根据用户的行业和邮件目的，提出针对的修改意见，能够提升邮件的专业性和效果
        5.输出格式：
        【润色后邮件】完整修改后的英文商务邮件文本
        【修改建议】针对邮件内容的具体修改意见和理由

    # Examples（示例）
       好的表达示例:"I am writing to you regarding the possibility of scheduling a meeting for next week."
       不好的表达示例:" I'm talking about the meeting scheduled for next week."

    # Constraints（约束）
        - 你的回答应该清晰、详细，并且易于理解。
        - 你应该提供具体的修改意见以便用户理解
        - 你的建议应该根据用户的目的来调整，并且符合英文商务邮件的写作规范和礼仪。
        - 不改变邮件原意并保持邮件关键信息不丢失，只改变表达方式""",

}             






def call_model(model_config: dict, prompt: str, system_prompt: str) -> dict:
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

st.sidebar.divider()

st.sidebar.title("Prompt 模板")
with st.sidebar.expander("选择一个 Prompt 模板", expanded=True):
    selected_prompt_template = st.selectbox("Prompt 模板", options=list(PROMPT_TEMPLATES.keys()), index=1)
    edited_prompt = st.text_area("编辑 Prompt（可修改）", value=PROMPT_TEMPLATES[selected_prompt_template], height=200)


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
                    results[key] = call_model(config, text, edited_prompt)

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
