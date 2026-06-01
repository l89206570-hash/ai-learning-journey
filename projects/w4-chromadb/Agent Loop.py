import os







# 1. 定义工具函数
def get_current_time():
    time_n
def calculate(expression: str):
      ...

  # 2. 工具描述（告诉 LLM 每个工具干什么）
TOOLS = [
    {"name": "get_current_time", "description": "这是一个可以获取当前时间的工具", "parameters": {...}},
    ...
]

  # 3. System Prompt
SYSTEM_PROMPT = """你是一个会在合适的时候使用工具回答助理 你可以使用以下工具：
...工具列表...
当你需要调用工具时，用这种格式：
{"tool": "工具名", "arguments": {...}}
当你准备好回答用户时，直接输出答案。
"""

  # 4. Agent 循环
def agent_loop(user_query):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    while True:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        reply = response.choices[0].message.content

          # 判断是工具调用还是最终答案
        if 工具调用:
            执行工具，结果追加到 messages
        else:
            return reply  # 最终答案