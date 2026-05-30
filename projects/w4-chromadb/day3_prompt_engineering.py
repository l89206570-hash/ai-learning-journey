# W4 Day 3 — Prompt Engineering 进阶：结构化五段法
"""
对比实验：凭感觉写 prompt vs 五段法 prompt

任务：让 LLM 把一段中文商品描述翻译成英文营销文案

三个版本：
  A. 裸奔 — 直接丢问题，无 system prompt
  B. 一句话 system prompt — "你是一个翻译助手"
  C. 五段法 — System/Context/Instruction/Examples/Constraints
"""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ═══════════════════════════════════════
# 测试数据
# ═══════════════════════════════════════

product_zh = """【云感T恤】夏季新款男士纯棉圆领短袖
面料：100% 新疆长绒棉，手感柔软亲肤
版型：微宽松落肩设计，不挑身材
颜色：雾霾蓝 / 炭黑 / 月白
价格：首发价 ¥129（原价 ¥199）"""

user_message = f"把这段商品描述翻译成英文营销文案，用于亚马逊 listing：\n\n{product_zh}"


# ═══════════════════════════════════════
# 三个版本的 prompt
# ═══════════════════════════════════════

# A. 裸奔 — 无 system prompt
prompt_a_system = ""

# B. 一句话 — 直觉型
prompt_b_system = "你是一个翻译助手，帮我把中文翻译成英文。"

# C. 五段法 — 结构化
prompt_c_system = """# System（角色定义）
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
- 描述中自然融入 2-3 个长尾关键词（如 "summer wardrobe essential""gift for boyfriend"）"""


# ═══════════════════════════════════════
# 测试
# ═══════════════════════════════════════

def test_prompt(label: str, system_prompt: str):
    start = time.time()
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    elapsed = time.time() - start
    content = response.choices[0].message.content.strip()
    tokens = response.usage.total_tokens

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  System prompt 长度: {len(system_prompt)} 字符 | 耗时: {elapsed:.1f}s | Token: {tokens}")
    print(f"{'='*60}")
    print(content[:500])
    if len(content) > 500:
        print(f"... (共 {len(content)} 字符)")
    return content


if __name__ == "__main__":
    print("Prompt Engineering 五段法 — 对比实验")
    print(f"测试问题：把商品描述翻译成英文营销文案\n")

    result_a = test_prompt("A. 裸奔（无 system prompt）", prompt_a_system)
    result_b = test_prompt("B. 一句话（直觉型）", prompt_b_system)
    result_c = test_prompt("C. 五段法（结构化）", prompt_c_system)

    print("\n\n>>> 对比要点：")
    print("  1. 标题是否有 SEO 关键词？")
    print("  2. 是否用 AIDA 结构？")
    print("  3. 是否编造了不存在的卖点？")
    print("  4. 是否符合亚马逊 listing 规范？")
    print("  5. 英文是否地道（非中式直译）？")
