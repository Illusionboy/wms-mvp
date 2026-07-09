"""客户名模糊匹配：子串 + 简繁体互认 + 拼音首字母。

纯函数，不依赖具体数据来源。调用方传入候选客户名列表（如
`CustomerAllocation.customer_name` 的去重结果），本模块判断 query 是否命中。

不处理日语假名读音 ↔ 汉字（如 "ヒガシウエ" ↔ "東上"）——公司名读音没有固定规则，
无法用算法推断，需要时应作为单独的人工别名功能。
"""
from __future__ import annotations

from pypinyin import lazy_pinyin
from zhconv import convert as zhconvert


def _to_simplified(text: str) -> str:
    return zhconvert(text, "zh-cn")


def _pinyin_initials(text: str) -> str:
    """汉字取拼音首字母，非汉字字符原样小写保留（用于"ZY"命中"哲艺"一类首字母搜索）。"""
    letters: list[str] = []
    for ch in text:
        if "一" <= ch <= "鿿":
            py = lazy_pinyin(ch)
            if py and py[0]:
                letters.append(py[0][0])
        elif ch.isalnum():
            letters.append(ch.lower())
    return "".join(letters)


def customer_name_matches(query: str, candidate: str) -> bool:
    """判断 query 是否模糊命中 candidate（客户名）。命中规则（任一满足即可）：

    1. 原始子串匹配，大小写不敏感（如"mm"命中"mm"，"澳门"命中"澳门优生活美妆"）
    2. 简体归一化后子串匹配——繁简互认（如"東上"/"东上"互相命中）
    3. candidate 的拼音首字母子串匹配纯字母 query（如"ZY"命中"哲艺"，"AM"命中"澳门优生活美妆"）
    """
    q = query.strip()
    if not q:
        return True
    q_lower = q.lower()
    c_lower = candidate.lower()
    if q_lower in c_lower:
        return True
    if _to_simplified(q).lower() in _to_simplified(candidate).lower():
        return True
    if q_lower.isalpha() and q_lower.isascii():
        if q_lower in _pinyin_initials(candidate).lower():
            return True
    return False


def resolve_customer_names(query: str, candidates: list[str]) -> list[str]:
    """从候选客户名列表中返回所有模糊命中 query 的客户名，保持原顺序、去重。"""
    seen: set[str] = set()
    result: list[str] = []
    for c in candidates:
        if c in seen:
            continue
        if customer_name_matches(query, c):
            seen.add(c)
            result.append(c)
    return result
