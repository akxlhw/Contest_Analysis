"""ICPC竞赛选手标签识别 - 配置模块"""

import re
import unicodedata

# ============================================================
# 列映射: 5组竞赛列 (名称, 时间, 级别, 等级)，1-based索引
# ============================================================
COMPETITION_COLUMNS = [
    (97, 98, 99, 100),   # CS, CT, CU, CV
    (101, 102, 103, 104), # CW, CX, CY, CZ
    (105, 106, 107, 108), # DA, DB, DC, DD
    (109, 110, 111, 112), # DE, DF, DG, DH
    (113, 114, 115, 116), # DI, DJ, DK, DL
]

# 学生基本信息列 (1-based)
STUDENT_INFO_COLUMNS = {
    "序号": 1,
    "姓名": 2,
    "学号": 3,
    "学院": 4,
}

# ============================================================
# 竞赛名称匹配 - 正则
# ============================================================
EC_FINAL_REGEX = re.compile(r'ec[\s\-_\.]?finals?', re.IGNORECASE)
WF_REGEX = re.compile(r'world[\s\-_\.]?finals?|(?<![a-zA-Z])wf(?![a-zA-Z])', re.IGNORECASE)

# ============================================================
# 竞赛名称匹配 - 关键词列表（兜底）
# ============================================================
DEFAULT_EC_FINAL_KEYWORDS = [
    "ec-final", "ec final", "ecfinal", "ec_final",
    "亚洲决赛", "亚洲ec决赛",
]

DEFAULT_WF_KEYWORDS = [
    "world final", "world-final", "worldfinal", "world_final",
    "wf", "w.f.",
    "世界总决赛", "全球总决赛",
]

# ============================================================
# 等级归一化映射
# ============================================================
DEFAULT_GRADE_ALIASES = {
    "金奖": ["金奖", "金牌", "金", "第一名", "一等", "一等奖", "冠军", "gold", "1st"],
    "银奖": ["银奖", "银牌", "银", "第二名", "二等", "二等奖", "亚军", "silver", "2nd"],
    "铜奖": ["铜奖", "铜牌", "铜", "第三名", "三等", "三等奖", "季军", "bronze", "3rd"],
}

# ============================================================
# 标签常量
# ============================================================
LABEL_TOP = "顶尖竞赛选手"
LABEL_EXCELLENT = "卓越竞赛选手"

# 标准等级集合
GOLD_GRADES = {"金奖"}
SILVER_GRADES = {"银奖"}
BRONZE_GRADES = {"铜奖"}


def normalize_grade(grade_str, grade_aliases=None):
    """等级归一化: 将各种写法统一为标准等级(金奖/银奖/铜奖)或None

    Args:
        grade_str: 原始等级字符串
        grade_aliases: 等级别名映射表，默认使用DEFAULT_GRADE_ALIASES

    Returns:
        "金奖"/"银奖"/"铜奖" 或 None
    """
    if grade_str is None:
        return None

    aliases = grade_aliases or DEFAULT_GRADE_ALIASES

    # 去空格 + Unicode归一化(NFKC) + lower()
    normalized = unicodedata.normalize("NFKC", str(grade_str).strip()).lower()

    if not normalized:
        return None

    for standard_grade, alias_list in aliases.items():
        for alias in alias_list:
            if unicodedata.normalize("NFKC", alias.strip()).lower() == normalized:
                return standard_grade

    return None


def match_competition_name(name, ec_keywords, wf_keywords):
    """双层匹配竞赛名称: 正则优先，关键词兜底

    Args:
        name: 竞赛名称字符串
        ec_keywords: EC-Final关键词列表
        wf_keywords: WF关键词列表

    Returns:
        "ec_final" / "wf" / None
    """
    if not name or not str(name).strip():
        return None

    name_str = str(name).strip()

    # 第一层: 正则匹配
    if EC_FINAL_REGEX.search(name_str):
        return "ec_final"
    if WF_REGEX.search(name_str):
        return "wf"

    # 第二层: 关键词兜底
    name_clean = unicodedata.normalize("NFKC", name_str.lower())
    # 去除空格/横线/点
    name_simplified = name_clean.replace(" ", "").replace("-", "").replace(".", "").replace("_", "")

    for kw in ec_keywords:
        kw_clean = unicodedata.normalize("NFKC", kw.lower()).replace(" ", "").replace("-", "").replace(".", "").replace("_", "")
        if kw_clean and kw_clean in name_simplified:
            return "ec_final"

    for kw in wf_keywords:
        kw_clean = unicodedata.normalize("NFKC", kw.lower()).replace(" ", "").replace("-", "").replace(".", "").replace("_", "")
        if kw_clean and kw_clean in name_simplified:
            return "wf"

    return None
