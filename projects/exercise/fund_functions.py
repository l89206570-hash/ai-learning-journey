# F1 — 函数基础（🔴 入职前必须）
#
# 每个函数补完函数体即可。自带测试，全部通过即完成。
# 运行：python projects/exercise/fund_functions.py

# ----------------------------------------------------------
# 1. 两数之和
# ----------------------------------------------------------
def add(a, b):
    return a+b


# ----------------------------------------------------------
# 2. 判断偶数（是偶数返回 True，否则 False）
# ----------------------------------------------------------
def is_even(n):
    if n%2 == 0 :
        result = True
    else:
        result = False 
    return result

# ----------------------------------------------------------
# 3. 打招呼：接收姓名，返回 "你好，{name}！"
# ----------------------------------------------------------
def greet(name):
    return f"你好，{name}！"

# ----------------------------------------------------------
# 4. 三个数取最大
# ----------------------------------------------------------
def max_of_three(a, b, c):
    return(max(a,b,c))





# ----------------------------------------------------------
# 5. 重复字符串：repeat("ha", 3) → "hahaha"
# ----------------------------------------------------------
def repeat(word, times):
    return(word*times)


# ----------------------------------------------------------
# 6. 统计单词：返回 {"原文字": text, "长度": len, "是否大写开头": bool}
#    提示：text[0].isupper() 判断首字母是否大写
# ----------------------------------------------------------
def word_info(text):
    return{"原文字":text, "长度":len(text), "是否大写开头":text[0].isupper()}


# ----------------------------------------------------------
# 7. 函数调函数
#    prices 是一个数字列表，对每个价格打 8 折后返回新列表
#    提示：在函数内部写 calc_discount，然后 [calc_discount(p) for p in prices]
# ----------------------------------------------------------
def apply_discount(prices):
    def calc_discount(p):
        return p*0.8
    return [calc_discount(p) for p in prices]


# ============================================================
# 测试（不用改）
# ============================================================
if __name__ == "__main__":
    assert add(3, 5) == 8, f"题1: add(3,5) = {add(3,5)}"
    assert add(-1, 1) == 0, f"题1: add(-1,1) = {add(-1,1)}"

    assert is_even(4) == True, f"题2: is_even(4) = {is_even(4)}"
    assert is_even(7) == False, f"题2: is_even(7) = {is_even(7)}"

    assert greet("小明") == "你好，小明！", f"题3: greet('小明') = {greet('小明')}"

    assert max_of_three(1, 5, 3) == 5, f"题4: max_of_three(1,5,3) = {max_of_three(1,5,3)}"
    assert max_of_three(7, 2, 7) == 7, f"题4: max_of_three(7,2,7) = {max_of_three(7,2,7)}"

    assert repeat("ha", 3) == "hahaha", f"题5: repeat('ha',3) = {repeat('ha',3)}"
    assert repeat("X", 1) == "X", f"题5: repeat('X',1) = {repeat('X',1)}"

    r = word_info("Hello")
    assert r["原文字"] == "Hello", f"题6: 原文字 = {r.get('原文字')}"
    assert r["长度"] == 5, f"题6: 长度 = {r.get('长度')}"
    assert r["是否大写开头"] == True, f"题6: 是否大写开头 = {r.get('是否大写开头')}"

    assert apply_discount([10, 20, 30]) == [8.0, 16.0, 24.0], f"题7: {apply_discount([10,20,30])}"

    print("F1 全部通过！")
