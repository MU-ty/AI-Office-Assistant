"""基础服务类"""

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List, Any

T = TypeVar('T')


class BaseService(Generic[T]):
    """所有服务的基类"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def get(self, id: int) -> Optional[T]:
        """获取单个对象"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有对象"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj: Any) -> T:
        """创建对象"""
        db_obj = self.model(**obj.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj: Any) -> Optional[T]:
        """更新对象"""
        db_obj = self.get(id)
        if db_obj:
            for key, value in obj.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """删除对象"""
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
