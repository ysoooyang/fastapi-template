import json
import pickle
import logging
from typing import Any, Optional, TypeVar, Callable, Union
from functools import wraps
from app.core.redis import get_async_redis

logger = logging.getLogger(__name__)
T = TypeVar("T")

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """生成缓存键
    
    Args:
        prefix: 缓存键前缀
        args: 位置参数
        kwargs: 关键字参数
        
    Returns:
        str: 生成的缓存键
    """
    key_parts = [prefix]
    
    # 添加位置参数
    for arg in args:
        key_parts.append(str(arg))
    
    # 添加关键字参数（按键排序）
    for k in sorted(kwargs.keys()):
        key_parts.append(f"{k}:{kwargs[k]}")
    
    return ":".join(key_parts)


def async_cache(prefix: str, expire: int = 3600):
    """异步缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        expire: 过期时间（秒）
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # 生成缓存键
                cache_key = generate_cache_key(prefix, *args, **kwargs)
                
                # 获取Redis客户端
                redis_client = await get_async_redis()
                
                # 尝试从缓存获取
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    try:
                        return pickle.loads(cached_data)
                    except Exception as e:
                        logger.debug(f"Pickle反序列化失败: {e}, 尝试JSON解析")
                        try:
                            return json.loads(cached_data)
                        except Exception as e:
                            logger.debug(f"JSON解析失败: {e}, 返回原始数据")
                            return cached_data
                
                # 缓存未命中，执行原函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                try:
                    await redis_client.setex(cache_key, expire, pickle.dumps(result))
                except Exception as e:
                    logger.debug(f"Pickle序列化失败: {e}, 尝试JSON序列化")
                    try:
                        await redis_client.setex(cache_key, expire, json.dumps(result))
                    except Exception as e:
                        logger.warning(f"缓存设置失败: {e}")
                
                return result
            except Exception as e:
                logger.error(f"异步缓存操作异常: {e}")
                # 出现异常时直接执行原函数
                return await func(*args, **kwargs)
        return wrapper
    return decorator


async def clear_cache(pattern: str = "*") -> int:
    """清除缓存
    
    Args:
        pattern: 缓存键模式，支持通配符，默认清除所有缓存
        
    Returns:
        int: 清除的缓存数量
    """
    try:
        redis_client = await get_async_redis()
        if not redis_client:
            logger.error("Redis连接失败，无法清除缓存")
            return 0
        
        keys = await redis_client.keys(pattern)
        if not keys:
            return 0
        
        count = await redis_client.delete(*keys)
        logger.info(f"已清除{count}个缓存: {pattern}")
        return count
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return 0 