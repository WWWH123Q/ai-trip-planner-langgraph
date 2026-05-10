"""POI相关API路由"""

import json
import re
from langchain_core.messages import SystemMessage, HumanMessage

from ...services.llm_service import get_llm
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...services.amap_service import get_amap_service
#get_amap_service 用于获取高德地图服务对象。
#get_unsplash_service 用于获取 Unsplash 图片服务对象。
from ...services.unsplash_service import get_unsplash_service
# POI 详情 / 搜索 → amap_service.py
# 景点图片 → unsplash_service.py
_photo_query_agent = None
_photo_cache = {}

PHOTO_QUERY_SYSTEM_PROMPT = """
你是一个旅游图片搜索词生成器。
你的任务是把中文城市名和中文景点名，转换成适合在 Unsplash 搜索图片的英文关键词。

要求：
1. 只输出 JSON 数组
2. 不要输出解释
3. 每个关键词必须是英文
4. 优先生成具体景点英文名
5. 如果景点不知名，就生成城市 + travel / landmark / museum / temple / architecture 等通用词

示例输入：
城市：南京
景点：南京博物院

示例输出：
["Nanjing Museum", "Nanjing China museum", "Nanjing architecture", "China museum"]
"""



def parse_json_array(text: str):
    """从模型输出中提取 JSON 数组"""
    try:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            return []

        data = json.loads(match.group(0))

        if not isinstance(data, list):
            return []

        return [
            item.strip()
            for item in data
            if isinstance(item, str) and item.strip()
        ]

    except Exception as e:
        print(f"⚠️ 解析图片搜索词失败: {e}")
        return []


def generate_photo_queries(name: str, city: str):
    """用 LangChain LLM 生成通用英文图片搜索词"""
    try:
        llm = get_llm()

        user_prompt = f"""
城市：{city}
景点：{name}

请生成 4 个适合 Unsplash 搜图的英文关键词。
只输出 JSON 数组。
"""

        response = llm.invoke([
            SystemMessage(content=PHOTO_QUERY_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ])

        result = response.content
        queries = parse_json_array(result)

        return queries

    except Exception as e:
        print(f"⚠️ LLM 生成图片搜索词失败: {e}")
        return []


def build_fallback_queries(name: str, city: str):
    """不用 LLM 时的兜底搜索词"""
    queries = []

    # 根据中文关键词推断类型
    if "博物" in name:
        queries.extend([
            "China museum",
            "Chinese museum architecture",
            "museum exhibition"
        ])

    if "寺" in name or "庙" in name:
        queries.extend([
            "Chinese temple",
            "China temple architecture",
            "traditional Chinese temple"
        ])

    if "湖" in name:
        queries.extend([
            "China lake travel",
            "Chinese lake scenery"
        ])

    if "山" in name:
        queries.extend([
            "China mountain travel",
            "Chinese mountain landscape"
        ])

    if "古城" in name or "城墙" in name:
        queries.extend([
            "Chinese ancient city wall",
            "China old town",
            "Chinese traditional architecture"
        ])

    # 最后兜底
    queries.extend([
        f"{city} China travel",
        f"{city} China landmark",
        "China travel landmark",
        "Chinese architecture",
        "China city travel"
    ])

    return queries


def unique_queries(queries):
    """去重并保留顺序"""
    seen = set()
    result = []

    for query in queries:
        if query and query not in seen:
            seen.add(query)
            result.append(query)

    return result[:8]

router = APIRouter(prefix="/poi", tags=["POI"])


class POIDetailResponse(BaseModel): #POI 详情响应模型 这个是专门给“POI 详情接口”用的返回格式。
    """POI详情响应
    返回大概长这样：
        {
      "success": true,
      "message": "获取POI详情成功",
      "data": {
        "name": "故宫博物院",
        "address": "北京市东城区景山前街4号"
      }
    }
    """
    success: bool
    message: str
    data: Optional[dict] = None #真正的 POI 详情数据，可以是 dict，也可以是 None


@router.get(#根据 POI ID 查询某个地点的详细信息。 比如访问：GET /api/poi/detail/B000A8UIN8
    "/detail/{poi_id}",
    #这个"/detail/{poi_id}"和前面的 ?city=北京 不一样。它表示 poi_id 是 URL 路径的一部分。
    # 比如：/api/poi/detail/123456
    # FastAPI 会自动把：123456传给函数：get_poi_detail(poi_id="123456") 这里的 poi_id 就来自 URL 路径
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取详细信息,包括图片"
)
async def get_poi_detail(poi_id: str):
    """
    获取POI详情
    
    Args:
        poi_id: POI ID
        
    Returns:
        POI详情响应
    """
    try:
        amap_service = get_amap_service() #获取高德服务包
        
        # 调用高德地图POI详情API
        result = amap_service.get_poi_detail(poi_id) #调用高德的POI详情方法：
        # 进入 amap_service.py 里的--> def get_poi_detail(self, poi_id: str):  --> 然后调用 MCP 工具：maps_search_detail
        
        return POIDetailResponse(
            success=True,
            message="获取POI详情成功",
            data=result
        )
        
    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取POI详情失败: {str(e)}"
        )


@router.get( #搜索POI
    "/search",
    summary="搜索POI",
    description="根据关键词搜索POI"
)
async def search_poi(keywords: str, city: str = "北京"):
    #根据关键词和城市搜索 POI。
    # 参数从 URL query 里来 async def search_poi(keywords: str, city: str = "北京"):
    # 这表示前端可以这样传：/ api / poi / search?keywords = 美术馆 & city = 南京
    """
    搜索POI

    Args:
        keywords: 搜索关键词
        city: 城市名称

    Returns:
        搜索结果
    """
    try:
        amap_service = get_amap_service() #调用高德工具包
        result = amap_service.search_poi(keywords, city) #调用高德搜索函数

        return {
            "success": True,
            "message": "搜索成功",
            "data": result
        }

    except Exception as e:
        print(f"❌ 搜索POI失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索POI失败: {str(e)}"
        )

@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称从Unsplash获取图片"
)
async def get_attraction_photo(name: str, city: str = ""):
    """
    获取景点图片

    Args:
        name: 景点名称
        city: 城市名称

    Returns:
        图片URL
    """
    try:
        # 先查缓存，避免反复请求 Unsplash 和 LLM
        cache_key = f"{city}:{name}"
        if cache_key in _photo_cache:
            return {
                "success": True,
                "message": "获取图片成功",
                "data": {
                    "name": name,
                    "photo_url": _photo_cache[cache_key]
                }
            }

        unsplash_service = get_unsplash_service()

        # 1. 先让 LLM 生成英文搜索词
        llm_queries = generate_photo_queries(name, city)

        # 2. 再准备通用兜底搜索词
        fallback_queries = build_fallback_queries(name, city)

        # 3. 合并搜索词，去重
        search_queries = unique_queries(llm_queries + fallback_queries)

        print(f"🔍 图片搜索词: {name} -> {search_queries}")

        photo_url = None

        for query in search_queries:
            photo_url = unsplash_service.get_photo_url(query)

            if photo_url:
                print(f"✅ 图片搜索成功: {name} -> {query}")
                break
            else:
                print(f"⚠️ 图片搜索无结果: {query}")

        # 写入缓存
        _photo_cache[cache_key] = photo_url

        return {
            "success": True,
            "message": "获取图片成功",
            "data": {
                "name": name,
                "photo_url": photo_url
            }
        }

    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}"
        )

# @router.get(
#     "/photo",
#     summary="获取景点图片",
#     description="根据景点名称从Unsplash获取图片"
# )
# async def get_attraction_photo(name: str): #根据景点名称，从 Unsplash 搜索一张图片 URL。
#     """
#     比如前端请求：GET /api/poi/photo?name=南京博物院
#     然后后端返回：
#     {
#       "success": true,
#       "message": "获取图片成功",
#       "data": {
#         "name": "南京博物院",
#         "photo_url": "https://..."
#       }
#     }
#
#     获取景点图片
#
#     Args:
#         name: 景点名称
#
#     Returns:
#         图片URL
#     """
#     try:
#         unsplash_service = get_unsplash_service()  #获取unsplash服务
#
#         # 搜索景点图片
#         photo_url = unsplash_service.get_photo_url(f"{name} China landmark") #先用“景点名 + China landmark”搜索 这样写的目的是让 Unsplash 更容易返回中国景点相关图片。
#
#         if not photo_url:
#             # 如果没找到,尝试只用景点名称搜索
#             photo_url = unsplash_service.get_photo_url(name)
#
#         return {
#             "success": True,
#             "message": "获取图片成功",
#             "data": {
#                 "name": name,
#                 "photo_url": photo_url
#             }
#         }
#     #返回图像结果：
#     # return {
#     #     "success": True,
#     #     "message": "获取图片成功",
#     #     "data": {
#     #         "name": name,
#     #         "photo_url": photo_url
#     #     }
#     # }
#
#     except Exception as e:
#         print(f"❌ 获取景点图片失败: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"获取景点图片失败: {str(e)}"
#         )
#POI：Point of Interest. 就是地图上一个“可以被搜索、可以被定位、可以被点击查看详情的地点”。
# POI 和普通地址有什么区别？
#
# 比如：南京市玄武区中山东路321号
# 这是一个地址。
#
# 而：南京博物院
# 这是一个 POI。
#
# POI 通常包含更多信息，比如：
#
# 名称：南京博物院
# 地址：南京市玄武区中山东路321号
# 类型：博物馆 / 景点
# 经纬度：118.xxx, 32.xxx
# 电话：xxx
# 营业时间：xxx
# 图片：xxx
# 评分：xxx
# POI ID：高德地图内部给它的唯一编号
#
# 所以你可以这样理解：
# 地址 = 一串位置描述
# POI = 地图系统里一个完整的地点对象
# 提问：POI 为什么重要？
#
# 因为地图服务不是只处理“文字”，它要处理“地点对象”。
#
# 比如你在前端搜索：南京 美术馆
# 高德地图可能返回多个 POI：
#     江苏省美术馆
#     金陵美术馆
#     南京艺术学院美术馆
#     某某画廊
# 每个 POI 都有自己的：
#     name
#     address
#     location
#     type
#     id
# 这样后端和前端才能进一步做事情：
#     在地图上打点
#     查看 POI 详情
#     规划去这个 POI 的路线
#     把它放进行程计划
#     显示景点卡片
#     获取图片





# 这个文件的整体流程
# /api/poi/detail/{poi_id}
#     ↓
# get_amap_service()
#     ↓
# amap_service.get_poi_detail()
#     ↓
# 返回 POI 详情
#
# /api/poi/search
#     ↓
# get_amap_service()
#     ↓
# amap_service.search_poi()
#     ↓
# 返回搜索结果
#
# /api/poi/photo
#     ↓
# get_unsplash_service()
#     ↓
# unsplash_service.get_photo_url()
#     ↓
# 返回图片 URL