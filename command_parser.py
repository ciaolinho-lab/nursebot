"""
指令解析器
==========
解析使用者輸入的聊天指令，支援：
  1. 直接全庫智慧查詢（無前綴，如：「導尿管」、「Metformin」、「糖尿病」）
  2. 精準前綴查詢（如：「護+主題」、「藥+學名」、「病+疾病」、「衛+主題」）
  3. 說明指令（如：「說明」、「幫助」、「help」）
"""

import re
from typing import Optional, Tuple

# 指令前綴與選單關鍵字對應表
COMMAND_MAP = {
    "護": "nursing_skill",
    "藥": "drug",
    "病": "disease",
    "衛": "education",
}

# 四格選單直接對應類別全覽
CATEGORY_KEYWORDS = {
    "護理": "nursing_skill",
    "護理技術": "nursing_skill",
    "藥物": "drug",
    "藥物查詢": "drug",
    "疾病": "disease",
    "臨床指引": "disease",
    "衛教": "education",
    "衛教單張": "education",
}

# 說明與選單關鍵字
HELP_KEYWORDS = {"說明", "幫助", "help", "選單", "menu", "?", "？", "hello", "你好", "嗨", "hi"}

# 指令分隔符號（支援 +、＋、:、：、空格）
SEPARATOR_PATTERN = re.compile(r"[+＋:：\s]")


def parse_command(text: str) -> Optional[Tuple[str, str]]:
    """
    解析使用者輸入的指令。

    Args:
        text: 使用者輸入的文字

    Returns:
        (command_type, keyword) 或 None（若為空字串）
    """
    text = text.strip()

    if not text:
        return None

    # 說明/幫助指令
    if text.lower() in HELP_KEYWORDS:
        return ("help", text)

    # 四格選單關鍵字 (護理, 藥物, 疾病, 衛教)
    if text in CATEGORY_KEYWORDS:
        return (CATEGORY_KEYWORDS[text], "ALL_CATEGORY")

    # 前綴精準查詢 (護/藥/病/衛)
    prefix = text[0]
    if prefix in COMMAND_MAP and len(text) > 1:
        rest = text[1:]
        # 檢查第二個字元是否為分隔符號
        if SEPARATOR_PATTERN.match(rest[0]):
            keyword = rest[1:].strip()
            if keyword:
                return (COMMAND_MAP[prefix], keyword)
            return None  # 如 "護+"、"藥:" 沒有關鍵字，回傳 None
        else:
            # 如 "護導尿管" 或 "藥Metformin"
            return (COMMAND_MAP[prefix], rest.strip())

    # 無前綴 -> 預設全庫智慧搜尋 (auto)
    return ("auto", text)

