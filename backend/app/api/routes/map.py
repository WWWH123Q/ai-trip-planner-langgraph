"""地图服务API路由
负责地图相关接口，比如 POI 搜索、天气查询、路线规划
它本身不直接调用高德 API，而是把请求交给：get_amap_service()
然后由backend/app/services/amap_service.py  去真正调用高德地图服务
"""

from fastapi import APIRouter, HTTPException, Query
#HTTPException：用来在接口出错时候返回HTTP错误
#Query：用来定义 GET 请求里的查询参数。
from typing import Optional
from ...models.schemas import (
    POISearchRequest,
    POISearchResponse,
    RouteRequest,
    RouteResponse,
    WeatherResponse
)
from ...services.amap_service import get_amap_service
#amap_service.py 获取高德地图服务实例
# map.py
# 接收前端请求
#     ↓
# get_amap_service()
#     ↓
# amap_service.py
# 真正调用高德地图 API
#     ↓
# 返回结果
#     ↓
# map.py 包装成 Response 返回前端

router = APIRouter(prefix="/map", tags=["地图服务"])
#创建路由对象，，这组接口的路径前面都加 /map，并且在接口文档里归类到“地图服务”。


@router.get(   #GET  /api/map/poi       搜索 POI
    "/poi",
    response_model=POISearchResponse,
    summary="搜索POI",
    description="根据关键词搜索POI(兴趣点)"
)
async def search_poi( #根据关键词和城市，搜索地图上的兴趣点。调用大概是： GET /api/map/poi?keywords=故宫&city=北京&citylimit=true
    keywords: str = Query(..., description="搜索关键词", example="故宫"),#keywords 是一个 URL 查询参数，类型是字符串，而且必填。
    city: str = Query(..., description="城市", example="北京"),
    citylimit: bool = Query(True, description="是否限制在城市范围内")
):
    """
    搜索POI
    
    Args:
        keywords: 搜索关键词
        city: 城市
        citylimit: 是否限制在城市范围内
        
    Returns:
        POI搜索结果
    """
    try:
        # 获取服务实例
        service = get_amap_service() #先拿到高德地图服务对象：给我一个可以调用高德地图功能的服务对象。
        # 执行之后，service 就变成了一个“高德地图服务工具箱”。
        
        # 真正执行搜索POI
        # 调用高德地图服务对象里的search_poi()方法，根据关键词、城市、是否限制城市范围，搜索地点列表。
        pois = service.search_poi(keywords, city, citylimit)  #再让这个服务对象去执行“搜索POI”的功能
        
        return POISearchResponse(
            success=True,
            message="POI搜索成功",
            data=pois
        )
    # 获取高德地图服务对象
    # ↓
    # 调用
    # service.search_poi()
    # ↓
    # 拿到
    # POI
    # 列表
    # pois
    # ↓
    # 包装成
    # POISearchResponse
    # ↓
    # 返回给前端
    except Exception as e: #如果POI搜索过程中报错，就返回500错误
        print(f"❌ POI搜索失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"POI搜索失败: {str(e)}"
        )


@router.get(  #GET  /api/map/weather   查询天气
    #当前端访问 GET /api/map/weather?city=北京 时，后端会调用高德地图服务查询北京天气，然后把结果包装成 WeatherResponse 返回给前端。
    "/weather",
    response_model=WeatherResponse, #意思是：这个接口返回的数据格式应该符合 WeatherResponse。
    summary="查询天气",
    description="查询指定城市的天气信息"
)#把下面这个函数注册成一个 GET 接口。
async def get_weather(
    city: str = Query(..., description="城市名称", example="北京")  #这个接口需要一个 URL 查询参数 city，类型是字符串，而且必填。“...”表示是必填
):
    """
    查询天气
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息
    """
    try:
        # 获取服务实例
        service = get_amap_service() #获得一个高德地图服务对象。得到一个高德工具箱。
        
        # 查询天气
        weather_info = service.get_weather(city)
        
        return WeatherResponse(
            success=True,
            message="天气查询成功",
            data=weather_info
        )
        
    except Exception as e:
        print(f"❌ 天气查询失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"天气查询失败: {str(e)}"
        )


@router.post( #POST /api/map/route 规划路线
    "/route",
    response_model=RouteResponse,
    summary="规划路线",
    description="规划两点之间的路线"
)
async def plan_route(request: RouteRequest):
    #request: RouteRequest 。前端传来的 JSON 请求体，会被 FastAPI 自动转换成 RouteRequest 对象。
    """
    规划路线
    
    Args:
        request: 路线规划请求
        
    Returns:
        路线信息
    """
    try:
        # 获取服务实例
        service = get_amap_service()
        
        # 规划路线 ：把前端传来的起点、终点、城市、路线类型交给高德地图服务，让它规划路线。
        route_info = service.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type
        )
        
        return RouteResponse(
            success=True,
            message="路线规划成功",
            data=route_info
        )
        
    except Exception as e:
        print(f"❌ 路线规划失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"路线规划失败: {str(e)}"
        )


@router.get( #GET  /api/map/health    检查地图服务是否正常
    "/health",
    summary="健康检查",
    description="检查地图服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查服务是否可用
        service = get_amap_service()
        
        return {
            "status": "healthy",
            "service": "map-service",
            "mcp_tools_count": len(service.mcp_tool._available_tools)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

