"""通用旅行规则检索器"""

from pathlib import Path
from typing import List, Dict, Any


RULE_FILE = Path(__file__).resolve().parent.parent / "knowledge_base" / "travel_rules.md"


def load_travel_rules() -> List[Dict[str, str]]:
    """
    读取 travel_rules.md，并按三级标题切分规则。
    """
    if not RULE_FILE.exists():
        return []

    text = RULE_FILE.read_text(encoding="utf-8")

    rules = []
    current_title = "通用规则"
    current_lines = []

    for line in text.splitlines():
        if line.startswith("### "):
            if current_lines:
                rules.append({
                    "title": current_title,
                    "content": "\n".join(current_lines).strip()
                })

            current_title = line.replace("### ", "").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        rules.append({
            "title": current_title,
            "content": "\n".join(current_lines).strip()
        })

    return rules


def build_rule_query_terms(
    preferences: List[str],
    free_text_input: str,
    weather_text: str
) -> List[str]:
    """
    根据用户偏好、补充要求、天气信息构造规则检索词。
    """
    terms = []

    terms.extend(preferences or [])

    if free_text_input:
        terms.append(free_text_input)

    if weather_text:
        terms.append(weather_text)

    text = " ".join(terms)

    # 天气相关
    if any(word in text for word in ["雨", "阵雨", "小雨", "中雨", "大雨", "雷阵雨"]):
        terms.extend(["雨天", "室内", "减少户外"])

    if any(word in text for word in ["高温", "炎热", "热", "30", "31", "32", "33", "34", "35"]):
        terms.extend(["高温", "下午", "室内", "减少暴晒"])

    if any(word in text for word in ["冷", "低温", "寒冷"]):
        terms.extend(["低温", "夜间", "保暖"])

    if any(word in text for word in ["大风", "风力", "风"]):
        terms.extend(["大风", "湖边", "山顶", "海边"])

    # 人群相关
    if any(word in text for word in ["老人", "父母", "长辈"]):
        terms.extend(["老人", "降低强度", "少步行"])

    if any(word in text for word in ["孩子", "亲子", "带娃", "儿童"]):
        terms.extend(["亲子", "孩子", "轻松"])

    if any(word in text for word in ["不想太累", "轻松", "慢节奏", "休闲"]):
        terms.extend(["轻松", "慢节奏", "每日景点数量"])

    # 景点偏好
    if any(word in text for word in ["博物馆", "博物", "展览", "美术馆"]):
        terms.extend(["博物馆", "上午", "2-3小时"])

    if any(word in text for word in ["夜景", "夜市", "灯光", "步行街"]):
        terms.extend(["夜景", "晚餐后"])

    if any(word in text for word in ["爬山", "山", "登高", "陵"]):
        terms.extend(["山岳", "体力", "恢复"])

    if any(word in text for word in ["古镇", "古街", "老街", "历史街区"]):
        terms.extend(["古镇", "古街", "慢走"])

    if any(word in text for word in ["美食", "小吃", "餐厅"]):
        terms.extend(["餐饮", "美食", "路线"])

    if any(word in text for word in ["低预算", "省钱", "便宜", "预算有限"]):
        terms.extend(["低预算", "免费", "经济型"])

    return terms


def score_rule(rule: Dict[str, str], terms: List[str]) -> int:
    """
    对规则进行简单关键词打分。
    """
    text = f"{rule.get('title', '')}\n{rule.get('content', '')}".lower()
    score = 0

    for term in terms:
        term = str(term).lower().strip()
        if not term:
            continue

        if term in text:
            score += 10

        for char in term:
            if char in text:
                score += 1

    return score


def retrieve_travel_rules(
    preferences: List[str],
    free_text_input: str,
    weather_text: str,
    top_k: int = 8
) -> str:
    """
    检索通用旅行规则。
    """
    rules = load_travel_rules()

    if not rules:
        return "暂无通用旅行规则。"

    terms = build_rule_query_terms(
        preferences=preferences,
        free_text_input=free_text_input,
        weather_text=weather_text
    )

    scored = []

    for rule in rules:
        score = score_rule(rule, terms)
        if score > 0:
            scored.append((score, rule))

    scored.sort(key=lambda x: x[0], reverse=True)

    selected = scored[:top_k]

    if not selected:
        # 没有命中特定规则时，给一些基础规则
        selected = [
            (0, rule)
            for rule in rules
            if rule["title"] in ["每日景点数量规则", "同区域优先规则", "首日和末日规则"]
        ]

    result = []

    for score, rule in selected:
        result.append(
            f"规则：{rule['title']}\n"
            f"{rule['content']}"
        )

    return "\n\n---\n\n".join(result)