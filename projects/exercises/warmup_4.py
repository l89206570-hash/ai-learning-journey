# W4 Day 6 暖身 — 函数 + JSON + Agent 基础巩固
"""
目标：趁热打铁，把 Day 5 遇到的函数/JSON 盲点练熟。
预计时间：20-30 分钟

练习规则：
- 每个练习有提示，先自己写，写不出来再看提示
- 可以翻 knowledge.md 看概念，不能看 day5 源码
- 运行 python projects/exercises/warmup_4.py 验证结果
"""

import json

# ============================================================
# 练习 1：写一个有参函数 + return
# ============================================================
"""
写一个函数 add_numbers(a, b)，接收两个数字，返回它们的和。
然后调用它，计算 3 + 5 并打印结果。

提示：
  - def 函数名(参数1, 参数2):
  - return 把值传出去
  - print(函数调用) 把返回值打印出来
"""

# TODO: 在这里写你的代码
def add_numbers(a, b):
    return a + b
print(add_numbers(3, 5))

# ============================================================
# 练习 2：区分 return 和 print
# ============================================================
"""
下面两个函数看起来很像，但行为不同。
请运行后解释：result_a 和 result_b 分别是什么？为什么？
"""

def get_value_a():
    return 42

def get_value_b():
    print(42)

result_a = get_value_a()
result_b = get_value_b()

# TODO: 打印 result_a 和 result_b，看看它们的值分别是什么
# print("result_a:", result_a)
# print("result_b:", result_b)
print("result_a:", result_a)
print("result_b:", result_b)
# TODO: 在这里写你的观察（用注释回答）
"""
return是把值给返回到函数里不直接显示在屏幕上，print是直接把值打印在屏幕上函数里没有值的存在
"""

# ============================================================
# 练习 3：JSON 字符串和字典互相转换
# ============================================================
"""
下面是一个 JSON 字符串（注意：它是字符串，不是字典）。
请完成两个任务：
  1. 用 json.loads 把它转成字典
  2. 从字典里取出 "name" 字段的值
  3. 新建一个字典，用 json.dumps 转成 JSON 字符串
"""

tool_response = '{"name": "get_word_length", "arguments": {"word": "hello"}}'

# TODO: 把 tool_response 转成字典
# parsed = ...
# print(parsed["name"])  # 应该输出 get_word_length
parsed = json.loads(tool_response)
print (parsed["name"])
# TODO: 新建字典 {"status": "ok", "count": 5}，转成 JSON 字符串
# new_json = ...
# print(new_json)  # 应该输出 {"status": "ok", "count": 5}
new_json=json.dumps ({"status": "ok", "count": 5})
print(new_json)
# ============================================================
# 练习 4：**dict 字典展开传参
# ============================================================
"""
给定一个函数和一个字典，用 ** 展开字典来调用函数。

理解：func(**{"word": "hello"}) 等价于 func(word="hello")
"""

def greet(name: str, greeting: str = "你好"):
    return f"{greeting}，{name}！"

params = {"name": "小明", "greeting": "早上好"}

# TODO: 用 **params 调用 greet 函数，并打印返回值
# result = ...
# print(result)
result = greet(**params)
print(result)

# ============================================================
# 练习 5：模拟 Agent 工具调用（综合练习）
# ============================================================
"""
这是 Day 5 Agent Loop 的精简版。给你：
  1. 一个工具函数
  2. 一个工具名到函数的映射字典
  3. 一个 LLM 返回的 tool_call（模拟）

请完成：解析 tool_call → 找到对应函数 → 执行 → 返回结果
"""

def double_number(n: int):
    """返回数字的两倍"""
    return n * 2

TOOL_MAP = {
    "double_number": double_number,
}

# 模拟 LLM 返回的工具调用（JSON 字符串）
llm_response = '{"name": "double_number", "arguments": {"n": 21}}'

# TODO: 完成以下步骤
# 1. 解析 JSON 字符串
# 2. 取出 name 和 arguments
# 3. 从 TOOL_MAP 找到函数
# 4. 用 **arguments 调用函数
# 5. 打印结果（应该是 42）
parseed = json.loads(llm_response)
tool_name = parseed["name"]
tool_args = parseed["arguments"]
func = TOOL_MAP[tool_name]
result = func(**tool_args)
print (result)
# ============================================================
# 运行所有测试
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("W4 Day 6 暖身练习")
    print("=" * 50)
    print()
    print("请完成上面每个 TODO 后运行本文件验证")
    print()
    print("提示：每完成一个练习就运行一次，确认输出是否符合预期")
