from typing import Optional
import aioredis
from redis import Redis, ConnectionPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis连接池
redis_pool: Optional[ConnectionPool] = None
# 同步Redis客户端
redis_client: Optional[Redis] = None
# 异步Redis客户端
async_redis_client: Optional[aioredis.Redis] = None


def create_redis_pool() -> ConnectionPool:
    """创建Redis连接池"""
    return ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
        decode_responses=True,
        encoding='utf-8',
        max_connections=10,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True
    )


def get_redis() -> Redis:
    """获取同步Redis客户端"""
    global redis_client, redis_pool
    try:
        if redis_client is None:
            if redis_pool is None:
                redis_pool = create_redis_pool()
            redis_client = Redis(connection_pool=redis_pool)
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise


async def get_async_redis() -> aioredis.Redis:
    """获取异步Redis客户端"""
    global async_redis_client
    try:
        if async_redis_client is None:
            async_redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding='utf-8',
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        return async_redis_client
    except Exception as e:
        logger.error(f"Async Redis connection error: {str(e)}")
        raise


async def init_redis_pool() -> None:
    """初始化Redis连接池"""
    global async_redis_client, redis_pool, redis_client
    try:
        # 初始化同步连接池
        if redis_pool is None:
            redis_pool = create_redis_pool()
            redis_client = Redis(connection_pool=redis_pool)
        
        # 初始化异步连接
        if async_redis_client is None:
            async_redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding='utf-8',
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
        
        # 测试连接
        await async_redis_client.ping()
        redis_client.ping()
        logger.info("Redis connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection pool: {str(e)}")
        raise


async def close_redis_pool() -> None:
    """关闭Redis连接池"""
    global async_redis_client, redis_client, redis_pool
    try:
        if async_redis_client is not None:
            await async_redis_client.close()
            async_redis_client = None
        
        if redis_client is not None:
            redis_client.close()
            redis_client = None
        
        if redis_pool is not None:
            redis_pool.disconnect()
            redis_pool = None
        
        logger.info("Redis connection pool closed successfully")
    except Exception as e:
        logger.error(f"Error closing Redis connection pool: {str(e)}")
        raise 