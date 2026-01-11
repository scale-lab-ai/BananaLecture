from functools import lru_cache
from typing import Generator, AsyncGenerator
from fastapi import Depends
from app.config import config_manager, AppConfig
from app.core.path_manager import PathManager, path_manager


@lru_cache()
def get_config() -> AppConfig:
    """Get application configuration dependency injection function"""
    return config_manager.get_config()


def get_config_manager():
    """Get configuration manager dependency injection function"""
    return config_manager


def get_path_manager() -> PathManager:
    """Get path manager dependency injection function"""
    return path_manager


# 示例：数据库连接依赖（如果将来需要）
async def get_db() -> AsyncGenerator:
    """
    获取数据库连接的依赖注入函数
    这里只是一个示例，实际项目中需要根据具体数据库实现
    """
    # 这里应该是实际的数据库连接逻辑
    # 例如：
    # async with AsyncSessionLocal() as session:
    #     yield session
    yield None


# 示例：当前用户依赖（如果将来需要认证）
async def get_current_user():
    """
    获取当前用户的依赖注入函数
    这里只是一个示例，实际项目中需要根据具体认证系统实现
    """
    # 这里应该是实际的认证逻辑
    # 例如：
    # token = dependencies.oauth2_scheme(request)
    # user = await get_user_from_token(token)
    # return user
    return None