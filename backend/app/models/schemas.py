"""数据模型定义"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import date


"""
BaseModel 是 Pydantic 的数据模型基类。
继承 BaseModel 后，你的类就具备：
1. 自动校验字段
2. 自动类型转换
3. 支持默认值
4. 支持嵌套模型
5. 支持转字典 model_dump()
6. 支持转 JSON model_dump_json()
7. 支持生成接口文档 schema
8. 支持被 FastAPI 自动用于请求和响应
"""


#
# 用户填写旅行需求（前端）
#         ↓
# TripRequest
#         ↓
# 多 Agent 系统处理
#         ↓
# TripPlan
#         ↓
# 返回给前端展示

# ============ 请求模型 ============
#前端传给后端的数据长什么样子
#重点理解：输入
class TripRequest(BaseModel):  #前端发给后端的旅行表单数据
    """旅行规划请求"""
    city: str = Field(..., description="目的地城市", example="北京")  #Field(...) 表示是必填字段，前端必须传city,不然就会报错
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD", example="2025-06-01")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD", example="2025-06-03")
    travel_days: int = Field(..., description="旅行天数", ge=1, le=30, example=3)  #ge=1,len=30 travel_days变量必须大于等于1且小于等于30
    transportation: str = Field(..., description="交通方式", example="公共交通")
    accommodation: str = Field(..., description="住宿偏好", example="经济型酒店")
    preferences: List[str] = Field(default=[], description="旅行偏好标签", example=["历史文化", "美食"])
    free_text_input: Optional[str] = Field(default="", description="额外要求", example="希望多安排一些博物馆")
    
    class Config:  #给接口文档看的，是给 FastAPI 自动生成的接口文档用的。而是接口文档里的示例数据。
                    # 它的作用是告诉 Pydantic / FastAPI：
                    # 当你生成接口文档时，给 TripRequest 展示一个示例请求体。
        json_schema_extra = {
            "example": {
                "city": "北京",
                "start_date": "2025-06-01",
                "end_date": "2025-06-03",
                "travel_days": 3,
                "transportation": "公共交通",
                "accommodation": "经济型酒店",
                "preferences": ["历史文化", "美食"],
                "free_text_input": "希望多安排一些博物馆"
            }
        }


class POISearchRequest(BaseModel):
    #继承了BaseModel，它是一个 Pydantic 模型。Pydantic 模型的作用是：校验数据格式、自动转换类型、给 FastAPI 生成接口文档
    # 比如前端传来JSON：
    # {
    #     "keywords": "故宫",
    #     "city": "北京",
    #     "citylimit": true
    # }
    # FastAPI会自动把它转换成：
    # request = POISearchRequest(
    #     keywords="故宫",
    #     city="北京",
    #     citylimit=True
    # )
    # 然后你就可以在代码里这样用：
    # request.keywords
    # request.city
    # request.citylimit

    """POI搜索请求：POI（Point of Interest，兴趣点/地图地点）
    在高德地图里，POI 可以是：天安门 北京大学 某家酒店 某家餐厅 某个地铁站
    这个类作用：当前端想让后端帮它搜索地图地点时，必须告诉后端：搜什么关键词、在哪个城市搜、要不要限制在这个城市范围内。
    """
    keywords: str = Field(..., description="搜索关键词", example="故宫")
    city: str = Field(..., description="城市", example="北京")
    citylimit: bool = Field(default=True, description="是否限制在城市范围内")  #默认是True


class RouteRequest(BaseModel):
    """路线规划请求"""
    origin_address: str = Field(..., description="起点地址", example="北京市朝阳区阜通东大街6号") #从哪里出发
    destination_address: str = Field(..., description="终点地址", example="北京市海淀区上地十街10号") #到哪去
    origin_city: Optional[str] = Field(default=None, description="起点城市")  #起点在哪个城市，可填可不填
    destination_city: Optional[str] = Field(default=None, description="终点城市")  #终点在哪个城市，可填可不填
    route_type: str = Field(default="walking", description="路线类型: walking/driving/transit") #用什么方式规划路线，默认是步行


# ============ 响应模型 ============
#后端返回给前端的数据长什么样子 或者  TripPlan 内部嵌套的数据长什么样
class Location(BaseModel):
    """地理位置"""
    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")
# 一个 Location 对象大概长这样：
# {
#   "longitude": 116.397,
#   "latitude": 39.908
# }


class Attraction(BaseModel):  #表示一个景点
    """景点信息
    一个景点类大概这样：
        {
      "name": "故宫博物院",
      "address": "北京市东城区景山前街4号",
      "location": {
        "longitude": 116.397,
        "latitude": 39.916
      },
      "visit_duration": 180,
      "description": "明清两代皇家宫殿，中国古代宫廷建筑精华。"
    }
    """
    name: str = Field(..., description="景点名称")
    address: str = Field(..., description="地址")
    location: Location = Field(..., description="经纬度坐标") #说明 Attraction 里面嵌套了一个 Location 对象。
    visit_duration: int = Field(..., description="建议游览时间(分钟)")
    description: str = Field(..., description="景点描述")
    category: Optional[str] = Field(default="景点", description="景点类别")  #Optional 表示可有可无
    rating: Optional[float] = Field(default=None, description="评分")
    photos: Optional[List[str]] = Field(default_factory=list, description="景点图片URL列表")
    #photos 是一个字符串列表如果没有传，就默认给一个空列表 []
    poi_id: Optional[str] = Field(default="", description="POI ID")
    image_url: Optional[str] = Field(default=None, description="图片URL")
    ticket_price: int = Field(default=0, description="门票价格(元)")


class Meal(BaseModel):
    """餐饮信息"""
    type: str = Field(..., description="餐饮类型: breakfast/lunch/dinner/snack")
    name: str = Field(..., description="餐饮名称")
    address: Optional[str] = Field(default=None, description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度坐标")
    description: Optional[str] = Field(default=None, description="描述")
    estimated_cost: int = Field(default=0, description="预估费用(元)")


class Hotel(BaseModel):
    """酒店信息"""
    name: str = Field(..., description="酒店名称")
    address: str = Field(default="", description="酒店地址")
    location: Optional[Location] = Field(default=None, description="酒店位置")
    price_range: str = Field(default="", description="价格范围")
    rating: str = Field(default="", description="评分")
    distance: str = Field(default="", description="距离景点距离")
    type: str = Field(default="", description="酒店类型")
    estimated_cost: int = Field(default=0, description="预估费用(元/晚)")


class DayPlan(BaseModel):
    """单日行程
    里面嵌套了：
    hotel: Optional[Hotel]
    attractions: List[Attraction]
    meals: List[Meal]
    一个 DayPlan 可以包含：一个推荐酒店、多个景点、多顿餐饮
    结构大概是：
    DayPlan
     ├── date
     ├── day_index
     ├── description
     ├── transportation
     ├── accommodation
     ├── hotel: Hotel
     ├── attractions: List[Attraction]
     └── meals: List[Meal]
     几个类不是孤立的，它们是层层嵌套的：
         DayPlan
     ├── hotel: Hotel
     │      └── location: Location
     ├── attractions: List[Attraction]
     │      └── location: Location
     └── meals: List[Meal]
            └── location: Location
    后面更大的 TripPlan 又会包含多个 DayPlan：
    TripPlan
     └── days: List[DayPlan]
     所以最终完整旅行计划大概是：
    TripPlan
     ├── 第一天 DayPlan
     │      ├── 酒店 Hotel
     │      ├── 景点 Attraction 列表
     │      └── 餐饮 Meal 列表
     ├── 第二天 DayPlan
     │      ├── 酒店 Hotel
     │      ├── 景点 Attraction 列表
     │      └── 餐饮 Meal 列表
     └── 第三天 DayPlan
            ├── 酒店 Hotel
            ├── 景点 Attraction 列表
            └── 餐饮 Meal 列表
    """
    date: str = Field(..., description="日期 YYYY-MM-DD")
    day_index: int = Field(..., description="第几天(从0开始)")
    description: str = Field(..., description="当日行程描述")
    transportation: str = Field(..., description="交通方式")
    accommodation: str = Field(..., description="住宿")
    hotel: Optional[Hotel] = Field(default=None, description="推荐酒店")
    attractions: List[Attraction] = Field(default=[], description="景点列表")
    meals: List[Meal] = Field(default=[], description="餐饮列表")


class WeatherInfo(BaseModel):
    """天气信息
        {
      "date": "2025-06-01",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 28,
      "night_temp": 20,
      "wind_direction": "东南风",
      "wind_power": "3级"
    }
    """
    date: str = Field(..., description="日期 YYYY-MM-DD")
    day_weather: str = Field(default="", description="白天天气")
    night_weather: str = Field(default="", description="夜间天气")
    day_temp: Union[int, str] = Field(default=0, description="白天温度")
    night_temp: Union[int, str] = Field(default=0, description="夜间温度")
    wind_direction: str = Field(default="", description="风向")
    wind_power: str = Field(default="", description="风力")

    # 下面这个是字段校验器：在 Pydantic 校验 day_temp 和 night_temp 之前，先调用 parse_temperature() 处理一下温度值。
    # 它专门负责把："28°C" "28℃" "28°" ---->  28
    @field_validator('day_temp', 'night_temp', mode='before')
    #对 day_temp 和 night_temp 这两个字段进行自定义校验/处理。
    #mode='before'在正式类型转换和字段校验之前，先执行这个函数。
    @classmethod
    def parse_temperature(cls, v):
        """解析温度,移除°C等单位"""
        if isinstance(v, str):
            # 移除°C, ℃等单位符号
            v = v.replace('°C', '').replace('℃', '').replace('°', '').strip()
            try:
                return int(v)
            except ValueError:
                return 0
        return v


class Budget(BaseModel):
    """预算信息"""
    total_attractions: int = Field(default=0, description="景点门票总费用")
    total_hotels: int = Field(default=0, description="酒店总费用")
    total_meals: int = Field(default=0, description="餐饮总费用")
    total_transportation: int = Field(default=0, description="交通总费用")
    total: int = Field(default=0, description="总费用")

#重点理解：最终输出，和前端接壤
# 业务数据本体：
# TripPlan、POIInfo、RouteInfo、WeatherInfo
# 接口响应外壳：
# TripPlanResponse、POISearchResponse、RouteResponse、WeatherResponse

class TripPlan(BaseModel): #真正的旅行计划本体
    """旅行计划
        TripPlan
     ├── city
     ├── start_date
     ├── end_date
     ├── days: List[DayPlan]
     │       ├── 第一天 DayPlan
     │       ├── 第二天 DayPlan
     │       └── 第三天 DayPlan
     ├── weather_info: List[WeatherInfo]
     ├── overall_suggestions
     └── budget: Budget
    """
    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    days: List[DayPlan] = Field(..., description="每日行程") #每个单日行程拼接起来成列表
    weather_info: List[WeatherInfo] = Field(default=[], description="天气信息")
    overall_suggestions: str = Field(..., description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算信息")


class TripPlanResponse(BaseModel): #旅行计划接口返回外壳，这个不是旅行计划本身，而是接口返回格式。
    """旅行计划响应
    作用是给前端一个统一结构：
        {
      "success": true,
      "message": "旅行计划生成成功",
      "data": {
        "city": "北京",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "days": [],
        "weather_info": [],
        "overall_suggestions": "建议提前预约热门景点",
        "budget": null
      }
    }
    """
    success: bool = Field(..., description="是否成功") #success：告诉前端是否成功
    message: str = Field(default="", description="消息") #message：给前端展示的提示信息
    data: Optional[TripPlan] = Field(default=None, description="旅行计划数据") #data：真正的 TripPlan 数据


class POIInfo(BaseModel): #一个地图地点的信息
    """POI信息"""
    id: str = Field(..., description="POI ID")
    name: str = Field(..., description="名称")
    type: str = Field(..., description="类型")
    address: str = Field(..., description="地址")
    location: Location = Field(..., description="经纬度坐标")
    tel: Optional[str] = Field(default=None, description="电话")


class POISearchResponse(BaseModel): #POI 搜索接口返回外壳
    """POI搜索响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: List[POIInfo] = Field(default=[], description="POI列表")


class RouteInfo(BaseModel): #一条路线的信息，这个表示路线规划结果本体。
    """路线信息"""
    distance: float = Field(..., description="距离(米)")
    duration: int = Field(..., description="时间(秒)")
    route_type: str = Field(..., description="路线类型")
    description: str = Field(..., description="路线描述")


class RouteResponse(BaseModel):#路线规划接口返回外壳
    """路线规划响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: Optional[RouteInfo] = Field(default=None, description="路线信息")


class WeatherResponse(BaseModel): #天气接口返回外壳
    # WeatherInfo = 某一天的天气
    # WeatherResponse = 一次天气查询返回的多天天气列表
    """天气查询响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: List[WeatherInfo] = Field(default=[], description="天气信息")


"""
常见的 API 设计方式。

统一格式是：
    {
      "success": true,
      "message": "xxx",
      "data": {}
    }
或者：
    {
      "success": false,
      "message": "错误原因",
      "data": null
    }
这样前端处理起来很方便。

前端不用猜接口有没有成功，只要看：response.success
然后再决定展示数据还是展示错误信息。

xxxInfo / xxxPlan = 真正的数据
xxxResponse = 接口返回外壳

这一组模型正好对应 README 里说的几个接口：

POST /api/trip/plan      → TripPlanResponse
GET /api/map/poi         → POISearchResponse
POST /api/map/route      → RouteResponse
GET /api/map/weather     → WeatherResponse

所以你的理解可以总结成：

这些类规定了后端返回给前端的数据格式。TripPlan 是核心旅行计划，TripPlanResponse 是包着它的接口响应；
POIInfo/RouteInfo/WeatherInfo 是地图、路线、天气数据本体，对应的 Response 类则是统一返回格式。
"""


# ============ 错误响应 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(default=False, description="是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(default=None, description="错误代码")

