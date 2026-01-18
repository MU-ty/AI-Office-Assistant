"""应用配置管理"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用全局配置"""
    
    # 应用基本信息
    APP_NAME: str = "Office Assistant Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/office_assistant"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL: int = 3600
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # LLM配置
    LLM_PROVIDER: str = "qwen"
    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-plus"
    OPENAI_API_KEY: str = ""
    
    # 文件存储配置
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 104857600  # 100MB
    
    # 外部服务配置
    TRANSLATION_API: str = "deepl"
    DEEPL_API_KEY: str = ""
    
    # 向量数据库配置
    VECTOR_DB_TYPE: str = "weaviate"
    WEAVIATE_URL: str = "http://localhost:8080"
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()
