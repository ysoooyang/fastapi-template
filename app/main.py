import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.exceptions import add_exception_handlers
from app.core.redis import init_redis_pool, close_redis_pool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 记录配置信息
logger.info(f"Project Name: {settings.PROJECT_NAME}")
logger.info(f"API Version: {settings.API_V1_STR}")
logger.info(f"Port: {settings.PORT}")

def create_application() -> FastAPI:
    """创建FastAPI应用程序实例"""
    application = FastAPI(
        title="FastAPI Template",
        description="""
        # FastAPI Template API文档
        
        ## 响应格式
        所有API响应均使用统一的JSON格式：
        ```json
        {
            "code": 0,  // 0表示成功，非0表示错误
            "msg": "操作成功",  // 响应消息
            "data": {}  // 响应数据
        }
        ```
        
        ## 错误码说明
        
        ### 通用错误 (1000-1999)
        - 0: 成功
        - 1000: 未知错误
        - 1001: 参数错误
        
        ### 认证错误 (2000-2999)
        - 2000: 认证失败，用户名或密码错误
        - 2001: 用户已存在
        - 2002: 无效的Token
        - 2003: 用户不存在
        - 2004: 用户未激活
        
        ### 权限错误 (3000-3999)
        - 3000: 权限不足
        - 3001: 角色不存在
        - 3002: 权限不存在
        
        ### 数据错误 (4000-4999)
        - 4000: 数据不存在
        - 4001: 数据已存在
        
        ### 系统错误 (5000-5999)
        - 5000: 系统错误
        - 5001: 数据库错误
        - 5002: 服务不可用
        
        ### 第三方服务错误 (6000-6999)
        - 6000: 第三方服务错误
        """,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # 配置CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加异常处理器
    add_exception_handlers(application)

    # 包含API路由
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # 启动事件
    @application.on_event("startup")
    async def startup_event():
        """应用启动时执行"""
        logger.info("Initializing application...")
        # 初始化Redis连接池
        await init_redis_pool()
        logger.info("Application initialized")

    # 关闭事件
    @application.on_event("shutdown")
    async def shutdown_event():
        """应用关闭时执行"""
        logger.info("Shutting down application...")
        # 关闭Redis连接池
        await close_redis_pool()
        logger.info("Application shutdown complete")

    return application

# 创建应用实例
app = create_application() 