# F2 — 数据结构操作（🔴 入职前必须）
#
# 补完每个函数的函数体。运行：python projects/exercise/fund_data_structures.py

# ----------------------------------------------------------
# 1. 取字典中某个 key 的值，如果 key 不存在返回默认值
#    提示：dict.get(key, default)
# ----------------------------------------------------------
def safe_get(d, key, default=None):
    result = d.get(key, default)
    return result


# ----------------------------------------------------------
# 2. 合并两个字典：把 b 的内容合并到 a 里，返回合并后的字典
#    提示：{**a, **b}
# ----------------------------------------------------------
def merge_dicts(a, b):
    return {**a, **b}


# ----------------------------------------------------------
# 3. 统计列表中每个元素出现的次数，返回 {"元素": 次数}
#    例：count_items(["a","b","a"]) → {"a": 2, "b": 1}
# ----------------------------------------------------------
def count_items(items):
    result = {}
    for item in items:
        result[item]= result.get(item, 0) + 1
    return result

# ----------------------------------------------------------
# 4. 取列表中前 N 个元素
#    提示：切片 lst[:n]
# ----------------------------------------------------------
def first_n(lst, n):
    peice = lst[:n]
    return peice


# ----------------------------------------------------------
# 5. 把字典的 key 和 value 互换（假设 value 唯一）
#    例：{"a": 1, "b": 2} → {1: "a", 2: "b"}
# ----------------------------------------------------------
def invert_dict(d):
    swap = {v : k for k, v in d.items() }
    return swap


# ----------------------------------------------------------
# 6. 提取嵌套字典中某个字段
#    data = {"user": {"name": "小明", "age": 25}}
#    get_nested(data, ["user", "name"]) → "小明"
#    提示：逐层深入 d[key]
# ----------------------------------------------------------
def get_nested(d, path):
    result = d
    for key in path :
        result= result[key]
    return result


# ----------------------------------------------------------
# 7. 按 value 排序字典，返回按值从大到小排列的 (key, value) 列表
#    提示：sorted(d.items(), key=lambda x: x[1], reverse=True)
# ----------------------------------------------------------
def sort_by_value(d):
    sort = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return sort 


# ============================================================
# 测试
# ============================================================
if __name__ == "__main__":
    assert safe_get({"a": 1}, "a") == 1, f"题1: safe_get({{'a':1}},'a') = {safe_get({'a':1},'a')}"
    assert safe_get({"a": 1}, "b") is None, f"题1: safe_get({{'a':1}},'b') = {safe_get({'a':1},'b')}"
    assert safe_get({"a": 1}, "b", 0) == 0, f"题1: default=0 → {safe_get({'a':1},'b',0)}"

    assert merge_dicts({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}, f"题2: {merge_dicts({'a':1},{'b':2})}"

    assert count_items(["a", "b", "a"]) == {"a": 2, "b": 1}, f"题3: {count_items(['a','b','a'])}"

    assert first_n([1, 2, 3, 4], 2) == [1, 2], f"题4: first_n([1,2,3,4],2) = {first_n([1,2,3,4],2)}"

    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}, f"题5: {invert_dict({'a':1,'b':2})}"

    data = {"user": {"name": "小明", "age": 25}}
    assert get_nested(data, ["user", "name"]) == "小明", f"题6: {get_nested(data,['user','name'])}"
    assert get_nested(data, ["user", "age"]) == 25, f"题6: age = {get_nested(data,['user','age'])}"

    assert sort_by_value({"a": 3, "b": 1, "c": 2}) == [("a", 3), ("c", 2), ("b", 1)], f"题7: {sort_by_value({'a':3,'b':1,'c':2})}"

    print("F2 全部通过！")
