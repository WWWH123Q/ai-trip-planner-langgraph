"""LangGraph 版本旅行规划 Agent"""

import json
import re
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict, Any, Optional

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from ..rules import travel_rules
from ..rules.travel_rules import retrieve_travel_rules

from ..models.schemas import (
    TripRequest,
    TripPlan,
    DayPlan,
    Attraction,
    Meal,
    WeatherInfo,
    Location,
    Hotel,
    Budget,
    POIInfo,
)
from ..services.llm_service import get_llm
from ..services.amap_service import get_amap_service
import math
from itertools import permutations

class TripState(TypedDict, total=False):
    """LangGraph 中流动的状态"""

    request: TripRequest
    trip_profile: Dict[str, Any]
    search_keywords: List[str]

    attractions: List[POIInfo]
    hotels: List[POIInfo]
    weather_info: List[WeatherInfo]

    route_plan: Dict[str, Any]
    route_plan_text: str

    travel_rules: str

    planner_text: str
    reflection_report: str
    trip_plan: TripPlan
    error: str


PLANNER_SYSTEM_PROMPT = """
你是一个专业旅行规划师。
你需要根据用户旅行需求、候选景点、候选酒店和天气信息，生成一个严格符合 JSON 格式的旅行计划。

重要要求：
1. 只输出 JSON，不要输出解释，不要输出 Markdown。
2. city/start_date/end_date 必须和用户请求一致。
3. days 数组长度必须等于 travel_days。
4. 每天安排 2-3 个景点。
5. 每天必须包含早、中、晚三餐。
6. 每个景点必须包含 name、address、location、visit_duration、description、category、ticket_price。
7. location 必须包含 longitude 和 latitude。
8. weather_info 必须包含每一天的天气信息。
9. budget 必须包含 total_attractions、total_hotels、total_meals、total_transportation、total。
10. 温度必须是纯数字，不要带 °C。

输出 JSON 结构如下：
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
"""

TRIP_PROFILE_SYSTEM_PROMPT = """
你是一个旅行需求分析助手。
你的任务是把用户的旅行请求整理成本次旅行画像 Trip Profile。

注意：
1. 只分析“本次旅行”，不要推断用户永久偏好。
2. 不要输出解释。
3. 只输出 JSON。
4. 如果信息不明确，用 "unspecified"。
5. search_keywords 用于后续地图 POI 搜索，必须给出 3-6 个中文关键词。

输出格式必须是：
{
  "city": "城市",
  "companions": "solo/friends/couple/parents/family/children/unspecified",
  "travel_intensity": "relaxed/normal/intensive/unspecified",
  "budget_level": "low/medium/high/unspecified",
  "theme_preferences": ["历史文化", "博物馆"],
  "mobility_constraints": ["减少长距离步行"],
  "daily_pace": "每天安排2个左右核心景点",
  "search_keywords": ["博物馆", "历史文化", "名胜古迹"],
  "planning_notes": ["优先选择交通便利的景点", "避免行程过满"]
}
"""

REFLECTION_SYSTEM_PROMPT = """
你是一个严格的旅行计划审查员。
你的任务是检查旅行计划是否合理，并在必要时修正它。

你需要重点检查：
1. 每天景点数量是否合理。
2. 用户如果要求轻松、不太累，行程是否过满。
3. 雨天是否安排了太多户外景点。
4. 高温天气是否安排了太多下午户外活动。
5. 博物馆、美术馆、展览馆是否适合安排在上午或下午前半段。
6. 夜景、夜市、古街、河畔是否适合安排在晚餐后。
7. 山岳、陵园、登高类景点是否和太多高强度步行景点放在同一天。
8. 同一天景点是否尽量位于同一区域，避免明显来回折返。
9. 每天是否包含早、中、晚三餐。
10. 是否包含酒店、预算、天气信息。
11. 是否满足用户偏好和额外要求。
12. JSON 字段结构是否完整。

输出要求：
1. 只输出 JSON。
2. 不要输出 Markdown。
3. 不要解释。
4. 必须输出以下结构：

{
  "has_issues": true,
  "issues": ["问题1", "问题2"],
  "fixed_plan": {
    "city": "...",
    "start_date": "...",
    "end_date": "...",
    "days": [],
    "weather_info": [],
    "overall_suggestions": "...",
    "budget": {}
  }
}

如果没有明显问题，也必须返回同样结构：
{
  "has_issues": false,
  "issues": [],
  "fixed_plan": 原始旅行计划JSON
}
"""

def _distance_km_by_location(loc_a: Location, loc_b: Location) -> float:
    """根据两个 Location 的经纬度计算直线距离，单位 km"""
    lon1 = loc_a.longitude
    lat1 = loc_a.latitude
    lon2 = loc_b.longitude
    lat2 = loc_b.latitude

    radius = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius * c


def _distance_km_between_pois(poi_a: POIInfo, poi_b: POIInfo) -> float:
    """计算两个 POI 之间的直线距离，单位 km"""
    return _distance_km_by_location(poi_a.location, poi_b.location)


def _poi_center(pois: List[POIInfo]) -> Optional[Location]:
    """计算一组 POI 的中心点"""
    if not pois:
        return None

    longitude = sum(poi.location.longitude for poi in pois) / len(pois)
    latitude = sum(poi.location.latitude for poi in pois) / len(pois)

    return Location(longitude=longitude, latitude=latitude)


def _filter_outlier_pois(
    pois: List[POIInfo],
    max_distance_from_center_km: float = 15.0
) -> List[POIInfo]:
    """剔除离核心区域太远的异常 POI"""
    if len(pois) <= 2:
        return pois

    center = _poi_center(pois)

    if not center:
        return pois

    filtered = []

    for poi in pois:
        distance = _distance_km_by_location(poi.location, center)

        if distance <= max_distance_from_center_km:
            filtered.append(poi)
        else:
            print(f"⚠️ 剔除离核心区域过远的景点: {poi.name}，距离中心约 {distance:.1f} km")

    return filtered or pois


def _group_pois_by_nearby_area(
    pois: List[POIInfo],
    travel_days: int,
    max_same_day_distance_km: float = 8.0
) -> List[List[POIInfo]]:
    """
    按空间距离把景点分组。
    目标：每天集中在一个小区域，减少跨区和回头路。
    """
    if not pois or travel_days <= 0:
        return []

    remaining = pois[:]
    day_groups = []

    for day_index in range(travel_days):
        if not remaining:
            day_groups.append([])
            continue

        seed = remaining.pop(0)
        group = [seed]

        nearby = sorted(
            remaining,
            key=lambda poi: _distance_km_between_pois(seed, poi)
        )

        target_count = 2

        for poi in nearby:
            if len(group) >= target_count:
                break

            max_distance_to_group = max(
                _distance_km_between_pois(poi, existing)
                for existing in group
            )

            if max_distance_to_group <= max_same_day_distance_km:
                group.append(poi)

        used_keys = {
            poi.id or f"{poi.name}-{poi.address}"
            for poi in group
        }

        remaining = [
            poi for poi in remaining
            if (poi.id or f"{poi.name}-{poi.address}") not in used_keys
        ]

        day_groups.append(group)

    return day_groups

def _group_center_distance_to_hotel(group: List[POIInfo], hotel: POIInfo) -> float:
    """计算一个景点组中心到酒店的距离"""
    center = _poi_center(group)
    if not center:
        return 999999

    return _distance_km_by_location(center, hotel.location)


def _choose_first_day_group_and_hotel(
    hotels: List[POIInfo],
    route_groups: List[List[POIInfo]]
) -> tuple[Optional[POIInfo], int]:
    """
    选择最适合作为第1天的区域：
    找到“酒店 - 景点组中心”距离最近的一组。
    返回：推荐酒店、首日 group 下标
    """
    if not hotels or not route_groups:
        return None, 0

    best_hotel = None
    best_group_index = 0
    best_distance = 999999

    for hotel in hotels:
        for index, group in enumerate(route_groups):
            if not group:
                continue

            distance = _group_center_distance_to_hotel(group, hotel)

            if distance < best_distance:
                best_distance = distance
                best_hotel = hotel
                best_group_index = index

    if best_hotel:
        print(
            f"🏨 第1天推荐酒店: {best_hotel.name}，"
            f"距离第1天区域中心约 {best_distance:.1f} km"
        )

    return best_hotel, best_group_index


def _move_group_to_first(route_groups: List[List[POIInfo]], first_index: int) -> List[List[POIInfo]]:
    """把最适合作为第1天的区域移动到第一位"""
    if not route_groups:
        return route_groups

    if first_index < 0 or first_index >= len(route_groups):
        return route_groups

    groups = route_groups[:]
    first_group = groups.pop(first_index)
    return [first_group] + groups

def _extract_json_object(text: str) -> Dict[str, Any]:
    """从模型输出中提取 JSON 对象"""
    try:
        text = text.strip()

        if text.startswith("```"):
            text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"^```", "", text).strip()
            text = re.sub(r"```$", "", text).strip()

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("模型输出中没有找到 JSON 对象")

        return json.loads(match.group(0))

    except Exception as e:
        raise ValueError(f"解析模型 JSON 失败: {e}\n原始输出:\n{text}")


def _poi_to_text(pois: List[POIInfo]) -> str:
    """把 POI 列表转成给 LLM 阅读的文本"""
    if not pois:
        return "暂无可用结果"

    lines = []
    for index, poi in enumerate(pois, start=1):
        lines.append(
            f"{index}. {poi.name} | 类型: {poi.type} | 地址: {poi.address} | "
            f"经纬度: {poi.location.longitude},{poi.location.latitude} | POI ID: {poi.id}"
        )

    return "\n".join(lines)

def _default_trip_profile(request: TripRequest) -> Dict[str, Any]:
    """当 LLM 解析失败时，使用规则生成一个默认 Trip Profile"""
    text = f"{request.free_text_input or ''} {' '.join(request.preferences or [])}"

    companions = "unspecified"
    if any(word in text for word in ["爸妈", "父母", "老人", "长辈"]):
        companions = "parents"
    elif any(word in text for word in ["孩子", "亲子", "带娃", "儿童"]):
        companions = "children"
    elif any(word in text for word in ["一个人", "独自", "自己"]):
        companions = "solo"
    elif any(word in text for word in ["朋友", "同学"]):
        companions = "friends"
    elif any(word in text for word in ["情侣", "对象", "女朋友", "男朋友"]):
        companions = "couple"

    travel_intensity = "normal"
    if any(word in text for word in ["不太累", "轻松", "慢节奏", "休闲"]):
        travel_intensity = "relaxed"
    elif any(word in text for word in ["安排满", "充实", "多逛", "特种兵"]):
        travel_intensity = "intensive"

    budget_level = "unspecified"
    if any(word in text for word in ["省钱", "低预算", "便宜", "经济"]):
        budget_level = "low"
    elif any(word in text for word in ["舒适", "品质", "高端"]):
        budget_level = "high"

    theme_preferences = request.preferences or ["景点"]

    search_keywords = []
    for pref in theme_preferences:
        if pref and pref not in search_keywords:
            search_keywords.append(pref)

    if "历史" in text or "文化" in text:
        search_keywords.extend(["博物馆", "历史文化", "名胜古迹"])
    if "美食" in text or "小吃" in text:
        search_keywords.extend(["步行街", "古街", "夜市"])
    if "夜景" in text:
        search_keywords.extend(["夜景", "步行街", "古街"])
    if "自然" in text or "公园" in text:
        search_keywords.extend(["公园", "自然风光"])
    if "拍照" in text:
        search_keywords.extend(["网红打卡", "观景"])

    if not search_keywords:
        search_keywords = ["景点"]

    # 去重并限制数量
    dedup_keywords = []
    for kw in search_keywords:
        if kw and kw not in dedup_keywords:
            dedup_keywords.append(kw)

    return {
        "city": request.city,
        "companions": companions,
        "travel_intensity": travel_intensity,
        "budget_level": budget_level,
        "theme_preferences": theme_preferences,
        "mobility_constraints": ["避免行程过满"] if travel_intensity == "relaxed" else [],
        "daily_pace": "每天安排1-2个核心景点" if travel_intensity == "relaxed" else "每天安排2-3个核心景点",
        "search_keywords": dedup_keywords[:6],
        "planning_notes": [
            "优先根据本次旅行画像规划，不要套用历史偏好。",
            "同一天景点尽量减少跨区域折返。"
        ]
    }


def _profile_to_text(profile: Dict[str, Any]) -> str:
    """把 Trip Profile 转成 prompt 可读文本"""
    if not profile:
        return "暂无本次旅行画像。"

    return json.dumps(profile, ensure_ascii=False, indent=2)

def _infer_amap_route_type(transportation: str) -> str:
    """根据用户选择的交通方式，推断高德路线规划类型"""
    text = transportation or ""

    if any(word in text for word in ["自驾", "开车", "驾车", "打车", "出租车"]):
        return "driving"

    if any(word in text for word in ["公共交通", "公交", "地铁", "轨道交通"]):
        return "transit"

    if any(word in text for word in ["步行", "徒步"]):
        return "walking"

    # 旅游城市内默认用公共交通更合理
    return "transit"


def _route_score(route_info: Dict[str, Any]) -> int:
    """
    路线排序分数：优先用真实耗时，耗时越短越顺路。
    """
    if not route_info:
        return 999999

    duration_s = route_info.get("duration_s")
    distance_m = route_info.get("distance_m")

    if duration_s and duration_s > 0:
        return int(duration_s)

    if distance_m and distance_m > 0:
        return int(distance_m)

    return 999999


def _order_pois_by_amap_nearest_neighbor(
    amap_service,
    pois: List[POIInfo],
    city: str,
    route_type: str,
    start_poi: Optional[POIInfo] = None
) -> List[POIInfo]:
    """
    用高德真实路线耗时做最近邻排序。
    从酒店或第一个景点出发，每次选择真实路线耗时最短的下一个景点。
    """
    if len(pois) <= 1:
        return pois

    remaining = pois[:]
    ordered = []

    if start_poi:
        current = start_poi
    else:
        current = remaining.pop(0)
        ordered.append(current)

    while remaining:
        best_poi = None
        best_score = 999999999

        for poi in remaining:
            route_info = amap_service.get_route_between_pois(
                origin_poi=current,
                destination_poi=poi,
                city=city,
                route_type=route_type
            )

            score = _route_score(route_info)

            if score < best_score:
                best_score = score
                best_poi = poi

        if best_poi is None:
            break

        ordered.append(best_poi)
        remaining.remove(best_poi)
        current = best_poi

    return ordered


def _split_route_by_day(
    ordered_pois: List[POIInfo],
    travel_days: int,
    travel_intensity: str = "normal"
) -> List[List[POIInfo]]:
    """
    把顺路排序后的景点分配到每天。
    relaxed：每天 2 个左右
    normal/intensive：每天 2-3 个
    """
    if travel_days <= 0:
        return []

    if travel_intensity == "relaxed":
        target_per_day = 2
    else:
        target_per_day = 3

    max_needed = travel_days * target_per_day
    selected = ordered_pois[:max_needed]

    day_groups = []
    index = 0

    for day in range(travel_days):
        remaining_days = travel_days - day
        remaining_pois = len(selected) - index

        if remaining_pois <= 0:
            day_groups.append([])
            continue

        count = max(1, min(target_per_day, math.ceil(remaining_pois / remaining_days)))
        day_groups.append(selected[index:index + count])
        index += count

    return day_groups


def _best_day_order_by_amap(
    amap_service,
    pois: List[POIInfo],
    city: str,
    route_type: str,
    start_poi: Optional[POIInfo] = None
) -> List[POIInfo]:
    """
    对一天内部的 2-3 个景点做精确排序。
    因为每天景点少，可以枚举所有排列，选择高德真实路线总耗时最短的一种。
    """
    if len(pois) <= 1:
        return pois

    best_order = pois
    best_score = 999999999

    for perm in permutations(pois):
        total_score = 0
        current = start_poi

        for poi in perm:
            if current is not None:
                route_info = amap_service.get_route_between_pois(
                    origin_poi=current,
                    destination_poi=poi,
                    city=city,
                    route_type=route_type
                )
                total_score += _route_score(route_info)

            current = poi

        # 景点之间路线
        for i in range(len(perm) - 1):
            route_info = amap_service.get_route_between_pois(
                origin_poi=perm[i],
                destination_poi=perm[i + 1],
                city=city,
                route_type=route_type
            )
            total_score += _route_score(route_info)

        if total_score < best_score:
            best_score = total_score
            best_order = list(perm)

    return best_order


def _route_plan_to_text(route_plan: Dict[str, Any]) -> str:
    """把路线优化结果转成 prompt 文本"""
    days = route_plan.get("days", [])

    if not days:
        return "暂无路线优化结果。"

    lines = []
    lines.append(f"路线策略：{route_plan.get('strategy', '')}")
    lines.append(f"路线方式：{route_plan.get('route_type', '')}")
    lines.append("")

    for day in days:
        day_index = day["day_index"]
        attractions = day["attractions"]

        lines.append(f"第{day_index + 1}天推荐顺路顺序：")

        for idx, attraction in enumerate(attractions, start=1):
            lines.append(
                f"{idx}. {attraction['name']} "
                f"({attraction['longitude']}, {attraction['latitude']})"
            )

        if day.get("route_notes"):
            lines.append("真实路线耗时：")
            lines.extend(day["route_notes"])

        lines.append("")

    return "\n".join(lines)

def _weather_to_text(weather_info: List[WeatherInfo]) -> str:
    """把天气列表转成文本"""
    if not weather_info:
        return "暂无天气信息"

    lines = []
    for w in weather_info:
        lines.append(
            f"{w.date}: 白天{w.day_weather} {w.day_temp}℃，"
            f"夜间{w.night_weather} {w.night_temp}℃，"
            f"{w.wind_direction} {w.wind_power}"
        )

    return "\n".join(lines)

def _is_valid_attraction_poi(poi: POIInfo) -> bool:
    """判断 POI 是否适合作为景点，而不是餐厅/酒店/商铺"""
    text = f"{poi.name} {poi.type} {poi.address}"

    bad_keywords = [
        "餐饮", "美食", "中餐", "西餐", "快餐", "咖啡", "茶饮",
        "小吃", "火锅", "烧烤", "面馆", "披萨", "汉堡", "料理",
        "酒店", "宾馆", "住宿", "公寓",
        "购物", "商场", "超市", "便利店",
        "公司", "写字楼", "住宅", "小区"
    ]

    good_keywords = [
        "风景名胜", "博物馆", "纪念馆", "美术馆", "展览馆",
        "公园", "动物园", "植物园", "寺", "庙", "宫",
        "古镇", "古街", "老街", "遗址", "陵", "山", "湖",
        "海滩", "沙滩", "观景", "景区", "旅游景点"
    ]

    if any(word in text for word in bad_keywords):
        return False

    if any(word in text for word in good_keywords):
        return True

    return True

def _apply_route_plan_to_trip_plan(trip_plan: TripPlan, route_plan: Dict[str, Any]) -> TripPlan:
    """
    用 route_plan 的顺路结果，强制重排 TripPlan 中每天的景点顺序。
    这样前端地图显示的顺序才会真正顺路，而不是只依赖 LLM 听不听话。
    """
    if not route_plan:
        return trip_plan

    route_days = route_plan.get("days", [])
    if not route_days:
        return trip_plan

    for day in trip_plan.days:
        # 找到对应 day_index 的 route day
        matched_route_day = None
        for route_day in route_days:
            if route_day.get("day_index") == day.day_index:
                matched_route_day = route_day
                break

        if not matched_route_day:
            continue

        route_attractions = matched_route_day.get("attractions", [])
        if not route_attractions:
            continue

        # route_plan 里的推荐顺序
        route_names = [
            item.get("name", "").strip()
            for item in route_attractions
            if item.get("name")
        ]

        if not route_names:
            continue

        # 建立 name -> order
        order_map = {
            name: index
            for index, name in enumerate(route_names)
        }

        # TripPlan 里已有景点
        original_attractions = day.attractions

        matched = []
        unmatched = []

        for attraction in original_attractions:
            attraction_name = attraction.name.strip()

            if attraction_name in order_map:
                matched.append(attraction)
            else:
                unmatched.append(attraction)

        matched.sort(key=lambda attraction: order_map.get(attraction.name.strip(), 9999))

        # 保留 LLM 额外生成但 route_plan 没覆盖的景点，放后面
        day.attractions = matched + unmatched

        # 顺手把 description 补一句路线说明
        if matched_route_day.get("area_note"):
            day.description = f"{day.description} 路线说明：{matched_route_day.get('area_note')}"

    return trip_plan
class LangGraphTripPlanner:
    """LangGraph 旅行规划系统"""

    def __init__(self):
        print("🔄 初始化 LangGraph 旅行规划系统...")
        self.llm = get_llm()
        self.amap_service = get_amap_service()
        self.graph = self._build_graph()
        print("✅ LangGraph 旅行规划系统初始化成功")

    def _build_graph(self):
        """构建 LangGraph 流程图"""
        builder = StateGraph(TripState)

        builder.add_node("trip_profile", self.trip_profile_node)
        builder.add_node("search_attractions", self.search_attractions_node)
        builder.add_node("search_weather", self.search_weather_node)
        builder.add_node("search_hotels", self.search_hotels_node)
        builder.add_node("route_optimizer", self.route_optimizer_node)
        builder.add_node("travel_rules", self.travel_rules_node)
        builder.add_node("generate_plan", self.generate_plan_node)
        builder.add_node("reflection_check", self.reflection_check_node)
        builder.add_node("validate_plan", self.validate_plan_node)

        builder.add_edge(START, "trip_profile")
        builder.add_edge("trip_profile", "search_attractions")
        builder.add_edge("search_attractions", "search_weather")
        builder.add_edge("search_weather", "search_hotels")
        builder.add_edge("search_hotels", "route_optimizer")
        builder.add_edge("route_optimizer", "travel_rules")
        builder.add_edge("travel_rules", "generate_plan")
        builder.add_edge("generate_plan", "reflection_check")
        builder.add_edge("reflection_check", "validate_plan")
        builder.add_edge("validate_plan", END)

        return builder.compile()

    def trip_profile_node(self, state: TripState) -> Dict[str, Any]:
            """节点：解析本次旅行画像"""
            request = state["request"]

            print("🧭 解析本次旅行画像 Trip Profile...")

            fallback_profile = _default_trip_profile(request)

            user_prompt = f"""
    用户旅行请求：
    - 城市：{request.city}
    - 开始日期：{request.start_date}
    - 结束日期：{request.end_date}
    - 旅行天数：{request.travel_days}
    - 交通方式：{request.transportation}
    - 住宿偏好：{request.accommodation}
    - 偏好标签：{", ".join(request.preferences) if request.preferences else "无"}
    - 额外要求：{request.free_text_input or "无"}

    请生成本次旅行画像。
    """

            try:
                response = self.llm.invoke([
                    SystemMessage(content=TRIP_PROFILE_SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt)
                ])

                profile = _extract_json_object(response.content)

                if not isinstance(profile, dict):
                    raise ValueError("Trip Profile 不是 JSON 对象")

                # 保底字段
                profile["city"] = request.city
                profile.setdefault("companions", fallback_profile["companions"])
                profile.setdefault("travel_intensity", fallback_profile["travel_intensity"])
                profile.setdefault("budget_level", fallback_profile["budget_level"])
                profile.setdefault("theme_preferences", fallback_profile["theme_preferences"])
                profile.setdefault("mobility_constraints", fallback_profile["mobility_constraints"])
                profile.setdefault("daily_pace", fallback_profile["daily_pace"])
                profile.setdefault("planning_notes", fallback_profile["planning_notes"])

                search_keywords = profile.get("search_keywords") or fallback_profile["search_keywords"]
                if not isinstance(search_keywords, list):
                    search_keywords = fallback_profile["search_keywords"]

                search_keywords = [
                    str(item).strip()
                    for item in search_keywords
                    if str(item).strip()
                ]

                if not search_keywords:
                    search_keywords = fallback_profile["search_keywords"]

                profile["search_keywords"] = search_keywords[:6]

                print("✅ Trip Profile 解析完成")
                print(_profile_to_text(profile))

                return {
                    "trip_profile": profile,
                    "search_keywords": profile["search_keywords"]
                }

            except Exception as e:
                print(f"⚠️ Trip Profile 解析失败，使用默认画像: {e}")
                print(_profile_to_text(fallback_profile))

                return {
                    "trip_profile": fallback_profile,
                    "search_keywords": fallback_profile["search_keywords"]
                }

    def search_attractions_node(self, state: TripState) -> Dict[str, Any]:
        """节点：根据 Trip Profile 搜索景点"""
        request = state["request"]

        profile = state.get("trip_profile", {})
        search_keywords = state.get("search_keywords") or profile.get("search_keywords") or request.preferences or [
            "景点"]

        print(f"🔍 根据 Trip Profile 搜索景点: {request.city}")
        print(f"搜索关键词: {search_keywords}")

        all_attractions = []
        seen = set()

        for keyword in search_keywords:
            pois = self.amap_service.search_poi(
                keywords=keyword,
                city=request.city,
                citylimit=True,
                limit=8,
            )

            for poi in pois:
                if not _is_valid_attraction_poi(poi):
                    continue

                key = poi.id or f"{poi.name}-{poi.address}"
                if key not in seen:
                    seen.add(key)
                    all_attractions.append(poi)

            if len(all_attractions) >= 15:
                break

        if not all_attractions:
            print("⚠️ Trip Profile 关键词无结果，改用'景点'搜索")
            all_attractions = self.amap_service.search_poi(
                keywords="景点",
                city=request.city,
                citylimit=True,
                limit=15,
            )

        print(f"✅ 搜索到候选景点数量: {len(all_attractions)}")

        return {"attractions": all_attractions[:15]}

    def search_weather_node(self, state: TripState) -> Dict[str, Any]:
        """节点2：查询天气"""
        request = state["request"]

        print(f"🌤️ 查询天气: {request.city}")
        weather_info = self.amap_service.get_weather(request.city)

        return {"weather_info": weather_info}

    def search_hotels_node(self, state: TripState) -> Dict[str, Any]:
        """节点3：搜索酒店"""
        request = state["request"]

        print(f"🏨 搜索酒店: {request.city}")
        hotels = self.amap_service.search_poi(
            keywords="酒店",
            city=request.city,
            citylimit=True,
            limit=8,
        )

        return {"hotels": hotels}

    def route_optimizer_node(self, state: TripState) -> Dict[str, Any]:
        """
        节点：按区域规划每天路线。
        规则：
        1. 第1天尽量选择离酒店近的区域，方便入住后游玩。
        2. 第2天以后不强求离酒店近，只要求当天景点集中在同一区域。
        3. 每天内部按顺路顺序游玩，减少回头路。
        """
        request = state["request"]
        attractions = state.get("attractions", [])
        hotels = state.get("hotels", [])
        trip_profile = state.get("trip_profile", {})

        print("🧭 开始区域化顺路路线优化...")

        if not attractions:
            print("⚠️ 没有候选景点，跳过路线优化")
            return {
                "route_plan": {"days": []},
                "route_plan_text": "暂无路线优化结果。"
            }

        route_type = _infer_amap_route_type(request.transportation)

        # 1. 控制候选景点数量，避免高德 API 调用过多
        candidate_limit = max(request.travel_days * 4, 8)
        candidate_attractions = attractions[:candidate_limit]

        # 2. 剔除明显离核心区域太远的异常点
        candidate_attractions = _filter_outlier_pois(
            candidate_attractions,
            max_distance_from_center_km=15.0
        )

        # 3. 先按地理邻近分组，每组就是一天主要游玩的区域
        route_groups = _group_pois_by_nearby_area(
            pois=candidate_attractions,
            travel_days=request.travel_days,
            max_same_day_distance_km=8.0
        )

        # 4. 选择第1天区域和推荐酒店
        start_hotel, first_group_index = _choose_first_day_group_and_hotel(
            hotels=hotels,
            route_groups=route_groups
        )

        # 5. 把离酒店最近的区域放到第1天
        route_groups = _move_group_to_first(route_groups, first_group_index)

        route_days = []

        for day_index, group in enumerate(route_groups):
            if not group:
                route_days.append({
                    "day_index": day_index,
                    "attractions": [],
                    "route_notes": [],
                    "distance_warnings": [],
                    "area_note": "当天没有足够的同区域景点候选。"
                })
                continue

            # 6. 第1天从酒店出发排序；其他天只做景点内部顺路排序
            if day_index == 0 and start_hotel:
                ordered_group = _order_pois_by_amap_nearest_neighbor(
                    amap_service=self.amap_service,
                    pois=group,
                    city=request.city,
                    route_type=route_type,
                    start_poi=start_hotel
                )
            else:
                # 非首日不以酒店为起点，只按景点之间距离顺路排序
                ordered_group = _order_pois_by_amap_nearest_neighbor(
                    amap_service=self.amap_service,
                    pois=group,
                    city=request.city,
                    route_type=route_type,
                    start_poi=None
                )

            attraction_items = []
            route_notes = []
            distance_warnings = []

            for poi in ordered_group:
                attraction_items.append({
                    "name": poi.name,
                    "address": poi.address,
                    "type": poi.type,
                    "longitude": poi.location.longitude,
                    "latitude": poi.location.latitude,
                    "poi_id": poi.id
                })

            # 7. 只有第1天计算酒店 -> 第一个景点
            if day_index == 0 and start_hotel and ordered_group:
                hotel_distance = _distance_km_between_pois(start_hotel, ordered_group[0])

                if hotel_distance > 8:
                    distance_warnings.append(
                        f"第1天酒店到第一个景点距离约 {hotel_distance:.1f} km，略远，建议选择更靠近该区域的酒店。"
                    )

                route_info = self.amap_service.get_route_between_pois(
                    origin_poi=start_hotel,
                    destination_poi=ordered_group[0],
                    city=request.city,
                    route_type=route_type
                )

                route_notes.append(
                    f"酒店 {start_hotel.name} → {ordered_group[0].name}：{route_info.get('summary')}"
                )

            # 8. 每天内部只计算景点之间路线
            for i in range(len(ordered_group) - 1):
                origin = ordered_group[i]
                destination = ordered_group[i + 1]

                straight_distance = _distance_km_between_pois(origin, destination)

                if straight_distance > 8:
                    distance_warnings.append(
                        f"{origin.name} → {destination.name} 直线距离约 {straight_distance:.1f} km，距离偏远，不建议放在同一天。"
                    )

                route_info = self.amap_service.get_route_between_pois(
                    origin_poi=origin,
                    destination_poi=destination,
                    city=request.city,
                    route_type=route_type
                )

                route_notes.append(
                    f"{origin.name} → {destination.name}：{route_info.get('summary')}"
                )

            # 9. 非首日增加区域说明，不要求离酒店近
            if day_index == 0:
                area_note = "第1天区域已尽量靠近推荐酒店，适合抵达后入住并开始游玩。"
            else:
                area_note = "本日按同区域景点集中安排；从酒店前往该区域后，尽量在区域内顺路游玩，不要求景点离酒店很近。"

            route_days.append({
                "day_index": day_index,
                "attractions": attraction_items,
                "route_notes": route_notes,
                "distance_warnings": distance_warnings,
                "area_note": area_note
            })

        route_plan = {
            "strategy": (
                "第1天优先选择离酒店较近的区域；"
                "后续每天按城市区域集中游玩，不要求每天离酒店近，"
                "但要求当天景点之间顺路、少回头路、少跨区。"
            ),
            "route_type": route_type,
            "hotel": {
                "name": start_hotel.name if start_hotel else "",
                "address": start_hotel.address if start_hotel else "",
                "longitude": start_hotel.location.longitude if start_hotel else None,
                "latitude": start_hotel.location.latitude if start_hotel else None,
            },
            "days": route_days
        }

        route_plan_text = _route_plan_to_text(route_plan)

        print("✅ 区域化顺路路线优化完成")
        print(route_plan_text[:1000])

        return {
            "route_plan": route_plan,
            "route_plan_text": route_plan_text
        }
    def travel_rules_node(self, state: TripState) -> Dict[str, Any]:
        """节点：检索通用旅行规划规则"""
        request = state["request"]
        weather_info = state.get("weather_info", [])

        weather_text = _weather_to_text(weather_info)

        print("📘 检索通用旅行规划规则")

        profile = state.get("trip_profile", {})

        profile_text = _profile_to_text(profile)

        rule_preferences = profile.get("theme_preferences") or request.preferences

        travel_rules = retrieve_travel_rules(
            preferences=rule_preferences,
            free_text_input=f"{request.free_text_input or ''}\n{profile_text}",
            weather_text=weather_text,
            top_k=8
        )

        print("✅ 通用旅行规则检索完成")
        print(travel_rules[:300])

        return {"travel_rules": travel_rules}

    def generate_plan_node(self, state: TripState) -> Dict[str, Any]:
        """节点4：调用 LLM 生成完整旅行计划"""
        request = state["request"]
        attractions = state.get("attractions", [])
        hotels = state.get("hotels", [])
        weather_info = state.get("weather_info", [])
        route_plan_text = state.get("route_plan_text", "")
        trip_profile = state.get("trip_profile", {})
        travel_rules = state.get("travel_rules", "")

        user_prompt = f"""
用户旅行需求：
- 城市：{request.city}
- 开始日期：{request.start_date}
- 结束日期：{request.end_date}
- 旅行天数：{request.travel_days}
- 交通方式：{request.transportation}
- 住宿偏好：{request.accommodation}
- 偏好标签：{", ".join(request.preferences) if request.preferences else "无"}
- 额外要求：{request.free_text_input or "无"}

本次旅行画像 Trip Profile：
{_profile_to_text(trip_profile)}

请优先遵守本次旅行画像。当前请求中的明确要求优先级最高，不要把其他旅行场景的偏好套用到本次旅行。

候选景点：
{_poi_to_text(attractions)}

路线顺路优化建议：
{route_plan_text}

路线规划硬性要求：
1. 第1天应优先使用 route_plan 中离酒店较近的区域，方便抵达、入住和开始游玩。
2. 第2天及以后，不要求景点离酒店很近，但要求当天景点集中在同一区域或相邻区域。
3. 每天景点应按照 route_plan_text 中的顺路顺序安排。
4. 不要把相距很远的景点放在同一天。
5. 不要为了凑景点数量而跨很远区域。
6. 如果 distance_warnings 提示距离偏远，应减少当天景点或更换为同区域景点。
7. 酒店只需要重点服务第1天和整体交通便利性，不要求每天都靠近酒店。

候选酒店：
{_poi_to_text(hotels)}

天气信息：
{_weather_to_text(weather_info)}

通用旅行规划规则：
{travel_rules}

请严格参考这些通用旅行规划规则，尤其是天气适配、行程强度、景点类型、路线顺序和特殊人群安排。

请基于以上信息生成完整旅行计划 JSON。
"""

        print("🧠 调用 LLM 生成旅行计划...")

        response = self.llm.invoke(
            [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
        )

        planner_text = response.content
        print("✅ LLM 已返回旅行计划文本")

        return {"planner_text": planner_text}

    def reflection_check_node(self, state: TripState) -> Dict[str, Any]:
            """节点：反思检查并修正旅行计划"""
            request = state["request"]
            planner_text = state.get("planner_text", "")
            travel_rules = state.get("travel_rules", "")
            route_plan_text = state.get("route_plan_text", "")
            weather_info = state.get("weather_info", [])

            print("🧐 开始 Reflection 检查旅行计划...")

            try:
                # 先尝试解析初版计划
                original_plan = _extract_json_object(planner_text)
            except Exception as e:
                print(f"⚠️ 初版计划 JSON 解析失败，跳过 Reflection，交给 validate_plan 兜底: {e}")
                return {
                    "planner_text": planner_text,
                    "reflection_report": f"初版计划 JSON 解析失败: {e}"
                }

            user_prompt = f"""
    用户旅行需求：
    - 城市：{request.city}
    - 开始日期：{request.start_date}
    - 结束日期：{request.end_date}
    - 旅行天数：{request.travel_days}
    - 交通方式：{request.transportation}
    - 住宿偏好：{request.accommodation}
    - 偏好标签：{", ".join(request.preferences) if request.preferences else "无"}
    - 额外要求：{request.free_text_input or "无"}

    天气信息：
    {_weather_to_text(weather_info)}

    通用旅行规划规则：
    {travel_rules}

    当前初版旅行计划 JSON：
    {json.dumps(original_plan, ensure_ascii=False, indent=2)}
    
    路线顺路优化建议：
    {route_plan_text}

路线检查要求：
1. 第1天是否尽量靠近推荐酒店。
2. 第2天及以后，不检查是否靠近酒店，只检查当天景点之间是否顺路、是否同区域。
3. 如果某天景点之间距离过远，应调整或减少景点。
4. 如果计划没有遵守 route_plan_text 的顺序，应在 fixed_plan 中修正。
5. 不要为了满足每天 2-3 个景点而牺牲路线合理性。

    请检查这个旅行计划是否违反用户需求、天气约束、通用旅行规则或字段完整性要求。
    如果有问题，请直接修正 fixed_plan。
    如果没有问题，请原样返回 fixed_plan。
    只输出 JSON。
    """

            try:
                response = self.llm.invoke([
                    SystemMessage(content=REFLECTION_SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt)
                ])

                reflection_text = response.content
                reflection_data = _extract_json_object(reflection_text)

                fixed_plan = reflection_data.get("fixed_plan")
                issues = reflection_data.get("issues", [])
                has_issues = reflection_data.get("has_issues", False)

                if not fixed_plan:
                    print("⚠️ Reflection 没有返回 fixed_plan，继续使用原始计划")
                    return {
                        "planner_text": json.dumps(original_plan, ensure_ascii=False),
                        "reflection_report": "Reflection 未返回 fixed_plan"
                    }

                print("✅ Reflection 检查完成")
                if has_issues:
                    print("🛠️ Reflection 发现并修正问题:")
                    for issue in issues:
                        print(f"  - {issue}")
                else:
                    print("✅ Reflection 未发现明显问题")

                return {
                    "planner_text": json.dumps(fixed_plan, ensure_ascii=False),
                    "reflection_report": "\n".join(issues) if issues else "未发现明显问题"
                }

            except Exception as e:
                print(f"⚠️ Reflection 检查失败，继续使用原始计划: {e}")
                return {
                    "planner_text": json.dumps(original_plan, ensure_ascii=False),
                    "reflection_report": f"Reflection 检查失败: {e}"
                }

    def validate_plan_node(self, state: TripState) -> Dict[str, Any]:
        """节点5：解析并校验 TripPlan"""
        request = state["request"]
        planner_text = state.get("planner_text", "")

        try:
            print("🔎 开始解析并校验 TripPlan JSON...")
            data = _extract_json_object(planner_text)

            # 强制修正核心字段，避免模型乱改
            data["city"] = request.city
            data["start_date"] = request.start_date
            data["end_date"] = request.end_date

            trip_plan = TripPlan(**data)

            if len(trip_plan.days) == 0:
                raise ValueError("days 为空")

            # 用 route_plan 强制重排每天景点顺序
            route_plan = state.get("route_plan", {})
            trip_plan = _apply_route_plan_to_trip_plan(trip_plan, route_plan)

            print("✅ TripPlan 校验通过，并已按 route_plan 强制重排景点顺序")
            return {"trip_plan": trip_plan}

        except Exception as e:
            print(f"❌ TripPlan 校验失败，启用兜底计划: {e}")
            fallback = self._create_fallback_plan(request, state)
            return {
                "trip_plan": fallback,
                "error": str(e),
            }

    def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        对外入口：保持和旧版 MultiAgentTripPlanner 一样。
        routes/trip.py 仍然可以调用 agent.plan_trip(request)。
        """
        print("\n" + "=" * 60)
        print("🚀 开始 LangGraph 旅行规划")
        print(f"目的地: {request.city}")
        print(f"日期: {request.start_date} 至 {request.end_date}")
        print(f"天数: {request.travel_days}")
        print("=" * 60 + "\n")

        final_state = self.graph.invoke({"request": request})

        trip_plan = final_state.get("trip_plan")
        if not trip_plan:
            return self._create_fallback_plan(request, final_state)

        return trip_plan

    def _create_fallback_plan(self, request: TripRequest, state: Optional[TripState] = None) -> TripPlan:
        """兜底计划：当 LLM 输出 JSON 失败时使用"""
        state = state or {}

        attractions = state.get("attractions", [])
        hotels = state.get("hotels", [])
        weather_info = state.get("weather_info", [])
        travel_rules = state.get("travel_rules", "")

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        days = []

        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            selected_attractions = attractions[i * 2:(i + 1) * 2]
            attraction_models = []

            for poi in selected_attractions:
                attraction_models.append(
                    Attraction(
                        name=poi.name,
                        address=poi.address,
                        location=poi.location,
                        visit_duration=120,
                        description=f"{poi.name}是{request.city}值得游览的地点。",
                        category=poi.type or "景点",
                        rating=None,
                        photos=[],
                        poi_id=poi.id,
                        image_url=None,
                        ticket_price=0,
                    )
                )

            if not attraction_models:
                attraction_models.append(
                    Attraction(
                        name=f"{request.city}城市漫游",
                        address=request.city,
                        location=Location(longitude=116.397128, latitude=39.916527),
                        visit_duration=120,
                        description=f"在{request.city}进行轻松城市游览。",
                        category="景点",
                        ticket_price=0,
                    )
                )

            hotel = None
            if hotels:
                h = hotels[0]
                hotel = Hotel(
                    name=h.name,
                    address=h.address,
                    location=h.location,
                    price_range="300-500元",
                    rating="",
                    distance="建议结合地图确认距离",
                    type=request.accommodation,
                    estimated_cost=400,
                )

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i + 1}天：{request.city}城市游览",
                transportation=request.transportation,
                accommodation=request.accommodation,
                hotel=hotel,
                attractions=attraction_models,
                meals=[
                    Meal(type="breakfast", name=f"第{i + 1}天早餐", description="当地特色早餐", estimated_cost=30),
                    Meal(type="lunch", name=f"第{i + 1}天午餐", description="午餐推荐", estimated_cost=60),
                    Meal(type="dinner", name=f"第{i + 1}天晚餐", description="晚餐推荐", estimated_cost=80),
                ],
            )

            days.append(day_plan)

        if not weather_info:
            weather_info = []

        total_attractions = 0
        total_hotels = request.travel_days * 400
        total_meals = request.travel_days * (30 + 60 + 80)
        total_transportation = request.travel_days * 80

        budget = Budget(
            total_attractions=total_attractions,
            total_hotels=total_hotels,
            total_meals=total_meals,
            total_transportation=total_transportation,
            total=total_attractions + total_hotels + total_meals + total_transportation,
        )

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=weather_info,
            overall_suggestions=f"这是为您生成的{request.city}{request.travel_days}日游兜底行程，建议出行前再次确认景点开放时间和交通情况。",
            budget=budget,
        )


_langgraph_trip_planner = None


def get_trip_planner_agent() -> LangGraphTripPlanner:
    """获取 LangGraph 旅行规划器，单例模式"""
    global _langgraph_trip_planner

    if _langgraph_trip_planner is None:
        _langgraph_trip_planner = LangGraphTripPlanner()

    return _langgraph_trip_planner