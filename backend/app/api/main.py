"""FastAPI主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#这个是处理 CORS 跨域问题的。
#前端 Vue 跑在 localhost:5173，后端 FastAPI 跑在 localhost:8000，浏览器会认为它们是不同来源。
# 为了让前端能请求后端，就需要配置 CORS。
from ..config import get_settings, validate_config, print_config
#get_settings：读取配置、validate_config：检查配置是否完整、print_config：打印配置信息
from .routes import trip, poi, map as map_routes
#导入三个路由模块，map as map_routes，因为map这个名字容易和python内置函数map()冲突，所以在这里改名字

# 获取配置
settings = get_settings()

# 创建FastAPI应用，创建整个后端应用，
# 名字是名字是 settings.app_name，版本是 settings.app_version，接口文档地址是 /docs 和 /redoc。
#启动后端后，你可以访问：http://localhost:8000/docs
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于HelloAgents框架的智能旅行规划助手API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS，这段是允许前端访问后端。告诉后端：允许指定的前端地址来请求我。
# 如果没有 CORS 配置，前端请求后端时，浏览器可能会拦截。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],  #表示允许所有请求方法：GET、POST、.....
    allow_headers=["*"],  #表示允许所有请求头。
)

# 注册路由,关键部分
#把 trip.py、poi.py、map.py 里面定义好的接口，挂载到主应用 app 上，并且统一加上 /api 前缀。
app.include_router(trip.router, prefix="/api")  #例如:把这个里面的路径/trip/plan 外面又增加了一层/api,现在整个路径/api/trip/plan
app.include_router(poi.router, prefix="/api")
app.include_router(map_routes.router, prefix="/api")

# app:一个 FastAPI 应用对象。这个对象里面提供了一个方法：app.on_event(...)
# 它可以用来注册一些“生命周期事件函数”。
# 所谓生命周期，就是：应用启动\应用运行中\应用关闭
# FastAPI 应用对象支持 "startup" 这个生命周期事件；当应用启动时，FastAPI 会自动执行所有注册到 "startup" 上的函数。
# 更准确地说，startup 不是你自己定义的随便一个字符串，而是 FastAPI/Starlette 约定好的事件名。
# 它认识这两个常见事件：@app.on_event("startup") 服务启动时执行
# @app.on_event("shutdown")@app.on_event("shutdown")

#定义 startup_event 函数，并把它注册到 app 的 startup 事件上
@app.on_event("startup")  #----->装饰器，下面的函数附加一个特殊身份。这是一个 FastAPI 启动事件函数
async def startup_event():#这个函数会在 FastAPI 应用启动时自动执行。
    #当运行main或者运行后端（uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000）时候就会自动执行，
    """应用启动事件"""
    print("\n" + "="*60)
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print("="*60)
    
    # 打印配置信息
    print_config()
    
    # 验证配置
    try:
        validate_config()  #检查配置是否完整
        print("\n✅ 配置验证通过")
    except ValueError as e:
        print(f"\n❌ 配置验证失败:\n{e}")
        print("\n请检查.env文件并确保所有必要的配置项都已设置")
        raise
    
    print("\n" + "="*60)
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("\n" + "="*60)
    print("👋 应用正在关闭...")
    print("="*60 + "\n")

# 这两个也是 API 接口，只是它们不是业务核心接口，而是两个很简单的“查看服务状态”的接口。
# 当有人用 GET 请求访问后端服务的根路径 / 时，就执行 root() 函数。
# 也就是你在浏览器里访问：http://localhost:8000/
# 后端就会返回：
#     {
#       "name": "应用名称",
#       "version": "应用版本",
#       "status": "running",
#       "docs": "/docs",
#       "redoc": "/redoc"
#     }
# 这个接口的作用是告诉你：后端服务已经启动了 应用叫什么 版本是多少 接口文档在哪里 所以它像一个“首页说明”。
@app.get("/") #把下面的 root() 函数注册成一个 GET 接口，路径是 /。 当浏览器访问GET / 就会调用root函数
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
##当有人用 GET 请求访问 /health 时，就执行 health() 函数。  即访问http://localhost:8000/health
#检查整个后端服务是否正常运行
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn #是一个 ASGI 服务器。
    
    uvicorn.run( #这句就是启动 FastAPI 服务。
        "app.api.main:app", #找到 app/api/main.py 这个模块然后找到里面名叫 app 的 FastAPI 对象
        host=settings.host,
        port=settings.port,
        reload=True   #表示开发模式下自动重载：修改代码后，uvicorn 会自动重启后端服务。
    )

# 如果当前 main.py 是被直接运行的
#     ↓
# 导入 uvicorn
#     ↓
# 启动 app.api.main 里的 app
#     ↓
# 使用 settings.host 作为地址
#     ↓
# 使用 settings.port 作为端口
#     ↓
# 开启代码修改后自动重载
