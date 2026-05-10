"""旅行规划API路由

本python总结：前端把 JSON 通过 POST /api/trip/plan 发给后端；
FastAPI 根据 TripRequest(BaseModel) 把 JSON 自动校验并转换成 TripRequest 对象；
然后后端把这个 request 传给多 Agent 系统；Agent 内部调用大模型和工具生成旅行计划；
最后后端把结果包装成 TripPlanResponse，FastAPI 再把它转成 JSON 返回给前端。

*前端用post发送请求；
后端处理完后，在同一请求里面返回response
这个response的数据格式是TripPlanResponse;
FastAPI会把TripPlanResponse自动序列化成json格式返回前端

前端 POST 给后端，后端 response 返回给前端
*区别
GET：我想拿数据
POST：我想提交数据，让后端处理
GET 和 POST 都会返回结果；GET 偏向“查询已有数据”，POST 偏向“提交数据并让后端处理、生成或创建结果”。

这个 trip.py 文件不是在写 Agent 逻辑，也不是在写前端页面，它是在写“后端对外提供的接口”。
前端点击按钮后，就是通过这里把请求发进后端，然后这里再调用 trip_planner_agent.py 生成旅行计划。
API:前端和后端之间的服务窗口
前端页面不能直接调用你的 Python 函数：agent.plan_trip(request)
因为前端是浏览器里的 Vue/JavaScript，后端是 Python/FastAPI。
所以中间需要一个“窗口”：
--------------------
前端页面
  ↓ 发送 HTTP 请求
API 接口
  ↓ 调用 Python 后端函数
Agent 系统
  ↓ 返回结果
API 接口
  ↓ 返回 JSON
前端页面展示
--------------------------
这个文件里的这两个：就是在定义一个 API 接口。
@router.post("/plan")
async def plan_trip(request: TripRequest):

这个py可以分成两个部分：
1. POST /trip/plan
   生成旅行计划

2. GET /trip/health
   检查服务是否正常
"""

from fastapi import APIRouter, HTTPException
#APIRouter:一个路由管理器，用来定义一组接口地址。
#HTTPException:当接口出错时，返回一个 HTTP 错误响应。
from ...models.schemas import (
    TripRequest, #前端传进来的旅行请求格式
    TripPlanResponse, #后端返回给前端的旅行计划响应格式
    ErrorResponse #错误响应格式
)

from ...agents.langgraph_trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"]) #这句是在创建一个路由对象。 prefix="/trip"这个 router 下面所有接口地址前面都自动加 /trip。
# router = 旅行规划接口文件夹
# 这个文件夹下面有两个接口：
# /trip/plan
# /trip/health
# #可以理解成：
# 我要创建一组和“旅行规划”有关的接口，
# 这些接口的地址前面都加上 /trip。
# 所以后面写：@router.post("/plan")
# 实际路径就是：/trip/plan
# 如果 main.py 里再统一加了 /api，最终就是：/api/trip/plan


#下面是核心：
# 为什么是 POST？
# 因为“生成旅行计划”需要前端提交一堆数据，比如：
#     {
#       "city": "北京",
#       "start_date": "2025-06-01",
#       "end_date": "2025-06-03",
#       "travel_days": 3,
#       "transportation": "公共交通",
#       "accommodation": "经济型酒店",
#       "preferences": ["历史文化", "美食"],
#       "free_text_input": "希望多安排一些博物馆"
#     }
# 这种“提交数据让后端处理”的操作，一般用 POST。
# 你可以简单记：
# GET：拿数据，比如查天气、查健康状态
# POST：提交数据，让后端生成/处理东西
@router.post(    #装饰器 @router.post ->把 plan_trip 这个函数交给 router，告诉 router：这个函数负责处理 /plan 这个 POST 请求。
    "/plan", #定义一个 POST 请求接口，地址是 /plan。结合前面的：prefix="/trip" 所以完整就是：POST/trip/plan
    response_model=TripPlanResponse, #这个接口返回给前端的数据，应该符合 TripPlanResponse 这个结构。
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    #这里定义了接口函数。
    # 把 plan_trip() 这个 Python 函数注册成一个 HTTP POST 接口，接口路径是 /trip/plan
    # 以后只要前端发送：POST / api / trip / plan
    # FastAPI 就会找到这个函数：async def plan_trip(request: TripRequest):然后自动执行它。
    # request: TripRequest.前端传来的 JSON 请求体，会被 FastAPI 自动转换成 TripRequest 对象。
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 获取Agent实例
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        print("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request) #调用类里面的函数，生成计划

        print("✅ 旅行计划生成成功,准备返回响应\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )

#第二个接口：健康检查：检查旅行规划服务是否正常启动，Agent 是否可以获取，工具数量是否正常。
@router.get(
    "/health",   #路径是:GET/api/trip/health
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()  #尝试是否能获取Agent,如果能获取，说明服务基本没错
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": "LangGraphTripPlanner",
            "engine": "langgraph"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )


#（1）完整流程：
# 前端点击“生成旅行计划”
#         ↓
# 前端发送 POST 请求到 /api/trip/plan
#         ↓
# FastAPI 找到 routes/trip.py 里的 plan_trip()
#         ↓
# FastAPI 把前端 JSON 转成 TripRequest
#         ↓
# 打印请求日志
#         ↓
# get_trip_planner_agent()
#         ↓
# 拿到多 Agent 系统
#         ↓
# agent.plan_trip(request)
#         ↓
# 生成 TripPlan
#         ↓
# TripPlanResponse(success=True, data=trip_plan)
#         ↓
# 返回 JSON 给前端
#         ↓
# 前端展示旅行计划

#（2）健康接口检查
# 浏览器/前端访问 /api/trip/health
#         ↓
# 调用 health_check()
#         ↓
# 尝试获取 Agent
#         ↓
# 返回服务状态和工具数量

# 现在可以把三个文件连起来：
# 1.schemas.py
# 定义数据结构：
# TripRequest / TripPlan / TripPlanResponse
#
# 2.trip_planner_agent.py
# 真正生成旅行计划：
# plan_trip(request) -> TripPlan
#
# 3.routes/trip.py
# 接口入口：
# 接收前端请求，调用 Agent，然后返回 TripPlanResponse

# 即       前端 JSON
#           ↓
#         routes/trip.py
#           ↓ 变成 TripRequest
#         trip_planner_agent.py
#           ↓ 生成 TripPlan
#         routes/trip.py
#           ↓ 包装成 TripPlanResponse
#         前端页面