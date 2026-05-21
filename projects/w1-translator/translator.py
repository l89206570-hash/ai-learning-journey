"""
W1 Day 1 — 带参数的命令行翻译工具

用法：
    uv run translator.py "你要翻译的文字"
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def translate(text: str, target_language: str = "日文") -> str:
    if not text.strip():
        """把中文翻译成日文"""
        return "[跳过] 空文本"           # 如果去掉空格后是空字符串
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是一个翻译助手，把中文翻译成{target_language}, **只输出翻译结果，不要添加任何解释、语气词或额外内容**。"},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[翻译失败] {e}"


def translate_file(input_path, output_path):
    stats = {"total": 0, "success": 0, "skipped": 0, "failed": 0}
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    with open(output_path, "w", encoding="utf-8") as outfile:
        for line in lines:
            text = line.rstrip("\n")
            if text == "":
                continue
            result = translate(text)
            stats["total"] += 1
            if result.startswith("[跳过]"):
                stats["skipped"] += 1
            elif result.startswith("[翻译失败]"):
                stats["failed"] += 1
            else:
                stats["success"] += 1
            outfile.write(f"{text} -> {result}\n")
    return stats

if __name__ == "__main__":
    stats =  translate_file("input.txt", "output.txt")
    print (f"翻译完成！总数: {stats['total']}, 成功: {stats['success']}, 跳过: {stats['skipped']}, 失败:{stats['failed']}")