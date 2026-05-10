"""POI相关API路由"""

import json
import re
from langchain_core.messages import SystemMessage, HumanMessage

from ...services.llm_service import get_llm
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...services.amap_service import get_amap_service
from ...services.unsplash_service import get_unsplash_service
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


class POIDetailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None #真正的 POI 详情数据，可以是 dict，也可以是 None


@router.get(
    "/detail/{poi_id}",
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
        

        result = amap_service.get_poi_detail(poi_id) #调用高德的POI详情方法：
        
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
        
        llm_queries = generate_photo_queries(name, city)

        fallback_queries = build_fallback_queries(name, city)

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


