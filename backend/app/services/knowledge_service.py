
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload

from app.models.knowledge import KnowledgeBase, Directory, Tag, document_tags
from app.models.document import Document
from app.utils.logger import get_logger
from app.services.search_service import search_service

logger = get_logger(__name__)

class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # =================
    # 知识库管理
    # =================
    async def create_knowledge_base(self, name: str, owner_id: int, description: str = None, is_public: bool = False) -> KnowledgeBase:
        kb = KnowledgeBase(
            name=name,
            description=description,
            owner_id=owner_id,
            is_public=is_public
        )
        self.db.add(kb)
        await self.db.commit()
        await self.db.refresh(kb)
        
        # 创建根目录
        root_dir = Directory(
            name="根目录",
            knowledge_base_id=kb.id,
            parent_id=None
        )
        self.db.add(root_dir)
        await self.db.commit()
        
        return kb

    async def list_knowledge_bases(self, user_id: int) -> List[KnowledgeBase]:
        # 暂时只返回自己拥有的，后续可扩展为有权限访问的
        query = select(KnowledgeBase).where(KnowledgeBase.owner_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    # =================
    # 目录管理
    # =================
    async def get_directory_tree(self, kb_id: int) -> List[Dict]:
        """获取目录树结构"""
        query = select(Directory).where(Directory.knowledge_base_id == kb_id).order_by(Directory.order)
        result = await self.db.execute(query)
        dirs = result.scalars().all()
        
        # 构建树
        dir_map = {d.id: {"id": d.id, "name": d.name, "parent_id": d.parent_id, "children": []} for d in dirs}
        tree = []
        
        for d in dirs:
            if d.parent_id and d.parent_id in dir_map:
                dir_map[d.parent_id]["children"].append(dir_map[d.id])
            else:
                tree.append(dir_map[d.id])
        
        return tree

    async def create_directory(self, name: str, kb_id: int, parent_id: Optional[int] = None) -> Directory:
        directory = Directory(
            name=name,
            knowledge_base_id=kb_id,
            parent_id=parent_id
        )
        self.db.add(directory)
        await self.db.commit()
        await self.db.refresh(directory)
        return directory

    async def move_directory(self, dir_id: int, new_parent_id: Optional[int], new_order: int = 0) -> Directory:
        """移动目录或排序"""
        query = select(Directory).where(Directory.id == dir_id)
        result = await self.db.execute(query)
        directory = result.scalars().first()
        if not directory:
            raise ValueError("目录不存在")
        
        # 检查循环引用 (简单的深度检查，或者递归检查祖先)
        if new_parent_id:
            parent_query = select(Directory).where(Directory.id == new_parent_id)
            parent_res = await self.db.execute(parent_query)
            parent = parent_res.scalars().first()
            # 这里的检查逻辑比较简单，实际生产需要防止将父节点移动到子节点下
            if parent and parent.knowledge_base_id != directory.knowledge_base_id:
                 raise ValueError("不能跨知识库移动")

        directory.parent_id = new_parent_id
        directory.order = new_order
        await self.db.commit()
        await self.db.refresh(directory)
        return directory

    # =================
    # 标签管理
    # =================
    async def create_tag(self, name: str, color: str = "#blue") -> Tag:
        # 检查是否存在
        query = select(Tag).where(Tag.name == name)
        result = await self.db.execute(query)
        existing = result.scalars().first()
        if existing:
            return existing
            
        tag = Tag(name=name, color=color)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def list_tags(self) -> List[Tag]:
        query = select(Tag)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_tags_to_document(self, doc_id: int, tag_names: List[str]):
        """为文档批量添加标签"""
        # 获取文档
        query = select(Document).where(Document.id == doc_id).options(selectinload(Document.tags))
        result = await self.db.execute(query)
        doc = result.scalars().first()
        if not doc:
            raise ValueError("文档不存在")
            
        # 获取或创建标签
        new_tags = []
        for name in tag_names:
            tag = await self.create_tag(name)
            new_tags.append(tag)
            
        # 更新关系
        # 简单的合并逻辑：追加不存在的
        current_tag_ids = {t.id for t in doc.tags}
        for tag in new_tags:
            if tag.id not in current_tag_ids:
                doc.tags.append(tag)
        
        await self.db.commit()

    async def delete_knowledge_base(self, kb_id: int, user_id: int):
        """删除知识库"""
        query = select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        result = await self.db.execute(query)
        kb = result.scalars().first()
        if not kb:
            raise ValueError("知识库不存在")
        if kb.owner_id != user_id:
             raise ValueError("无权删除此知识库")
        
        # 清理 ES 中的索引
        doc_query = select(Document).where(Document.knowledge_base_id == kb_id)
        doc_result = await self.db.execute(doc_query)
        for doc in doc_result.scalars().all():
            try:
                await search_service.delete_document(doc.id)
            except Exception as e:
                logger.error(f"清理 ES 索引失败 (doc_id={doc.id}): {e}")

        await self.db.delete(kb)
        await self.db.commit()

    async def delete_directory(self, dir_id: int):
        """删除目录及其内容"""
        # 使用递归删除
        await self._delete_directory_recursive(dir_id)
        await self.db.commit()

    async def _delete_directory_recursive(self, dir_id: int):
        # 1. 删除该目录下的所有文档 (逐个删除以触发 ORM 级联和 ES 清理)
        result = await self.db.execute(select(Document).where(Document.directory_id == dir_id))
        docs = result.scalars().all()
        for doc in docs:
            try:
                await search_service.delete_document(doc.id)
            except Exception as e:
                logger.error(f"清理 ES 索引失败 (doc_id={doc.id}): {e}")
            await self.db.delete(doc)
        
        # 2. 查找子目录
        result = await self.db.execute(select(Directory).where(Directory.parent_id == dir_id))
        children = result.scalars().all()
        
        # 3. 递归删除子目录
        for child in children:
            await self._delete_directory_recursive(child.id)
            
        # 4. 删除自身
        await self.db.execute(delete(Directory).where(Directory.id == dir_id))

