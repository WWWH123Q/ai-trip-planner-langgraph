

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




@router.post(   
    "/plan",
    response_model=TripPlanResponse, 
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
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

@router.get(
    "/health",   #路径是:GET/api/trip/health
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()  
        
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

