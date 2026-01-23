from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # 验证连接是否有效
    pool_size=20,
    max_overflow=0,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """
    数据库会话依赖注入函数
    用于 FastAPI 依赖注入系统
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
