"""
核心配置模块 - 环境变量和应用配置
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # ============================================================
    # 基本配置
    # ============================================================
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 应用信息
    APP_NAME: str = "办公助手Agent"
    APP_VERSION: str = "1.0.0"
    
    # ============================================================
    # 数据库配置
    # ============================================================
    
    # 数据库类型: sqlite (开发) 或 postgresql (生产)
    DB_TYPE: str = "sqlite"  # 改为 "postgresql" 使用 PostgreSQL
    
    # PostgreSQL (生产)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "office_assistant"
    
    # SQLite (开发)
    SQLITE_DB_PATH: str = "./data/office_assistant.db"
    
    @property
    def DATABASE_URL(self) -> str:
        """动态生成数据库 URL"""
        if self.DB_TYPE == "postgresql":
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:  # sqlite
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"
    
    SQLALCHEMY_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1小时
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # ============================================================
    # JWT认证配置
    # ============================================================
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ============================================================
    # CORS配置
    # ============================================================
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    
    # ============================================================
    # 文件上传配置
    # ============================================================
    
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS: List[str] = [
        "pdf", "txt", "docx", "xlsx", "pptx",
        "mp3", "wav", "m4a", "webm", "mp4"
    ]
    
    # ============================================================
    # AI/ML配置
    # ============================================================
    
    # Hugging Face模型
    HF_MODEL_DEVICE: str = "cuda"  # 或 "cpu"
    
    # 文本摘要模型
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    
    # NER模型
    NER_MODEL: str = "en_core_web_sm"
    
    # 向量化模型
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # 翻译API
    TRANSLATION_API: str = "google"  # 或 "deepl", "azure"
    DEEPL_API_KEY: str = ""
    GOOGLE_TRANSLATE_API_KEY: str = ""
    
    # LLM API
    OPENAI_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""
    QWEN_API_KEY: str = ""
    
    # ============================================================
    # 任务队列配置 (Celery)
    # ============================================================
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    
    # ============================================================
    # 日志配置
    # ============================================================
    
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ============================================================
    # 邮件配置
    # ============================================================
    
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@office-assistant.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
