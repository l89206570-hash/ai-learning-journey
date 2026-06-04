# F3 — JSON & 序列化（🔴 入职前必须）
#
# 补完每个函数体。运行：python projects/exercise/fund_json.py

import json

# ----------------------------------------------------------
# 1. 把字典转成 JSON 字符串
#    提示：json.dumps(d, ensure_ascii=False)
# ----------------------------------------------------------
def to_json(d):
    return json.dumps(d, ensure_ascii=False)


# ----------------------------------------------------------
# 2. 把 JSON 字符串转成 Python 字典
#    提示：json.loads(s)
# ----------------------------------------------------------
def from_json(s):
    return json.loads(s)


# ----------------------------------------------------------
# 3. 把字典写入 JSON 文件
#    提示：json.dump(d, f, ensure_ascii=False, indent=2)
# ----------------------------------------------------------
def save_json(d, filepath):
    with open(filepath, "w") as f:
        return json.dump(d,f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------
# 4. 从 JSON 文件读取字典
#    提示：json.load(f)
# ----------------------------------------------------------
def load_json(filepath):
    with open(filepath, "r") as f:    
        return json.load(f)


# ----------------------------------------------------------
# 5. 模拟 API 响应：把一个列表包装成 {"status": "ok", "data": 列表, "count": 长度}
#    然后转成 JSON 字符串
#    例：wrap_response([1,2,3]) → '{"status":"ok","data":[1,2,3],"count":3}'
# ----------------------------------------------------------
def wrap_response(items):
    result = {"status":"ok", "data":items, "count":len(items)}
    return json.dumps(result)



# ----------------------------------------------------------
# 6. 模拟解析 API 返回的工具调用参数
#    tool_call_json = '{"name":"calculate","args":{"expression":"3+5"}}'
#    返回调用名和参数字典：("calculate", {"expression": "3+5"})
#    提示：先 json.loads，再取 name 和 args 两个字段
# ----------------------------------------------------------
def parse_tool_call(tool_call_json):
    change = json.loads(tool_call_json)
    result = (change.get("name"), change.get("args"))
    return result
    


# ============================================================
# 测试
# ============================================================
if __name__ == "__main__":
    d1 = {"name": "小明", "age": 25}
    s1 = to_json(d1)
    assert s1 == '{"name": "小明", "age": 25}', f"题1: {s1}"

    d2 = from_json('{"a": 1, "b": 2}')
    assert d2 == {"a": 1, "b": 2}, f"题2: {d2}"

    import os, tempfile
    tmp = os.path.join(tempfile.gettempdir(), "test_f3.json")
    save_json({"x": 100}, tmp)
    assert os.path.exists(tmp), "题3: 文件未创建"
    d3 = load_json(tmp)
    assert d3 == {"x": 100}, f"题4: {d3}"
    os.remove(tmp)

    r5 = wrap_response([1, 2, 3])
    assert r5 == '{"status": "ok", "data": [1, 2, 3], "count": 3}', f"题5: {r5}"

    name, args = parse_tool_call('{"name":"calculate","args":{"expression":"3+5"}}')
    assert name == "calculate", f"题6 name: {name}"
    assert args == {"expression": "3+5"}, f"题6 args: {args}"

    print("F3 全部通过！")
