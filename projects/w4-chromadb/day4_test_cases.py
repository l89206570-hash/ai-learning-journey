# W4 Day 4 — Prompt 固定测试集
"""
  3 条测试，每次改 prompt 后跑一遍，确保改动没有破坏已有能力。

  测试格式：每一条 = (场景, 用户输入, system prompt, 检查函数)
  检查函数接收 call_model 返回的 dict，返回 (通过/不通过, 原因)
  """

import sys
sys.path.insert(0, "F:/ai-learning-journey/projects/w2-model-battle")
from battle import call_model, MODELS, PROMPT_TEMPLATES

  # 用 DS V4 Flash 跑测试（快 + 便宜）
MODEL = MODELS["deepseek-v4-flash"]


def check_contains(result, keywords):
    """Helper：检查输出是否包含指定关键词"""
    if not result["success"]:
        return False, f"调用失败: {result.get('error')}"
    for kw in keywords:
        if kw not in result["content"]:
            return False, f"缺少 '{kw}'"
    return True, "通过"


  # ═══════════════════════════════
  # 测试用例（你来定义 3 条）
  # ═══════════════════════════════

TEST_CASES = [
("场景1: 翻译功能测试",
    "请将以下中文商品描述翻译成英文listing文案: 使用华为智慧屏S3 Pro增强您的家庭娱乐体验。其智能双核处理器和240Hz HONOR显示屏可提供令人惊叹的视觉效果，而超级投影功能可实现低延迟、高帧率的屏幕共享。这款 75 英寸 4K 电视具有人工智能驱动的儿童看护和健身选项，以及无缝连接和语音控制，非常适合全家人使用。",
PROMPT_TEMPLATES["prompt_translate_system"],
lambda result: check_contains(result, ["Title", "Bullet Points", "Description"]),
"期望：输出包含 Title、Bullet Points 和 Description 三个部分的英文 listing 文案",
),
  
("场景2：bug修复测试",
    "请修复以下代码中的错误: def add_numbers(a, b):\n    return a - b",
    PROMPT_TEMPLATES["prompt_code_system"],
    lambda result: check_contains(result, ["错误"]),
    "期望：输出包含错误描述和修复建议",
),

      # 格式：(场景名, 用户输入, system_prompt, 检查函数, 期望说明)
      # TODO: 你来写 3 条

("场景3：推理测试",
    "如果所有的猫都会爬树，而汤姆是一只猫，那么汤姆会爬树吗？请解释你的推理过程。",
    PROMPT_TEMPLATES["prompt_reasoning_system"],
    lambda result: check_contains(result, ["汤姆", "爬树", "推理"]),
    "期望：输出包含汤姆、爬树和推理过程的回答"
)
]

  # 跑测试
if __name__ == "__main__":
    for i, (name, user_input, system_prompt, check_fn, expect) in enumerate(TEST_CASES, 1):
        print(f"\n{'='*50}")
        print(f"  测试 {i}: {name}")
        print(f"  输入: {user_input[:50]}...")
        print(f"  期望: {expect}")
        result = call_model(MODEL, user_input, system_prompt)
        passed, reason = check_fn(result)
        status = "PASS" if passed else "FAIL"
        print(f"  结果: {status} — {reason}")