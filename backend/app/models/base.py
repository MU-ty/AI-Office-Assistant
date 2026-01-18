"""基础模型类"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, func
from app.db import Base as SQLAlchemyBase


class BaseModel(SQLAlchemyBase):
    """所有模型的基础类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
