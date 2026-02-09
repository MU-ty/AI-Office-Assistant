
import asyncio
import sys
import os
from sqlalchemy import select, delete

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import async_session, init_db
from app.models.user import User
from app.models.knowledge import KnowledgeBase
from app.models.document import Document
from app.services.knowledge_service import KnowledgeService
from app.services.document_service import DocumentService
from app.services.search_service import search_service
from fastapi import UploadFile
from io import BytesIO

async def test_isolation():
    print("=== 开始测试知识库数据隔离 ===")
    
    # 初始化数据库
    await init_db()
    
    async with async_session() as db:
        # 1. 准备测试用户
        query = select(User).where(User.username == "iso_test_user")
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            user = User(username="iso_test_user", email="iso@test.com", hashed_password="pwd")
            db.add(user)
            await db.commit()
            await db.refresh(user)
        print(f"测试用户: {user.username} (ID: {user.id})")
        
        # 2. 创建两个隔离的知识库
        ks = KnowledgeService(db)
        kb1 = await ks.create_knowledge_base("KB_Alpha", user.id)
        kb2 = await ks.create_knowledge_base("KB_Beta", user.id)
        print(f"创建知识库: {kb1.name} (ID: {kb1.id}), {kb2.name} (ID: {kb2.id})")
        
        # 3. 分别上传文档
        ds = DocumentService(db)
        
        file1 = UploadFile(filename="alpha_doc.txt", file=BytesIO(b"Content for Alpha"))
        doc1 = await ds.create_document("Alpha Doc", file1, user.id, kb_id=kb1.id)
        # 模拟后台处理完成
        await ds.process_document_background(doc1['id'])
        print(f"上传文档到 KB_Alpha: {doc1['title']} (ID: {doc1['id']})")
        
        file2 = UploadFile(filename="beta_doc.txt", file=BytesIO(b"Content for Beta"))
        doc2 = await ds.create_document("Beta Doc", file2, user.id, kb_id=kb2.id)
        await ds.process_document_background(doc2['id'])
        print(f"上传文档到 KB_Beta: {doc2['title']} (ID: {doc2['id']})")
        
        # 4. 测试列表隔离性
        print("\n--- 测试列表隔离性 ---")
        
        # 查询 KB1
        list1 = await ds.list_documents(0, 100, None, user.id, knowledge_base_id=kb1.id)
        ids1 = [d['id'] for d in list1]
        print(f"查询 KB_Alpha 文档列表: {len(list1)} 个 - IDs: {ids1}")
        if doc1['id'] in ids1 and doc2['id'] not in ids1:
            print("✅ KB_Alpha 列表隔离测试通过")
        else:
            print(f"❌ KB_Alpha 列表隔离失败! 包含了: {ids1}")
            
        # 查询 KB2
        list2 = await ds.list_documents(0, 100, None, user.id, knowledge_base_id=kb2.id)
        ids2 = [d['id'] for d in list2]
        print(f"查询 KB_Beta 文档列表: {len(list2)} 个 - IDs: {ids2}")
        if doc2['id'] in ids2 and doc1['id'] not in ids2:
            print("✅ KB_Beta 列表隔离测试通过")
        else:
            print(f"❌ KB_Beta 列表隔离失败! 包含了: {ids2}")

        # 5. 测试搜索隔离性 (依赖 ES)
        print("\n--- 测试搜索隔离性 ---")
        # 给 ES 一点时间索引
        await asyncio.sleep(2) 
        
        # 在 KB1 中搜 "Content" (两者都有)
        search_res1 = await search_service.search("Content", filters={"knowledge_base_id": kb1.id})
        search_ids1 = [item['id'] for item in search_res1['items']]
        print(f"在 KB_Alpha 中搜索 'Content': 找到 {len(search_ids1)} 个 - IDs: {search_ids1}")
        
        if doc1['id'] in search_ids1 and doc2['id'] not in search_ids1:
             print("✅ KB_Alpha 搜索隔离测试通过")
        else:
             print(f"❌ KB_Alpha 搜索隔离失败 (可能 ES 未启动或延迟)")

        # 在 KB2 中搜 "Content"
        search_res2 = await search_service.search("Content", filters={"knowledge_base_id": kb2.id})
        search_ids2 = [item['id'] for item in search_res2['items']]
        print(f"在 KB_Beta 中搜索 'Content': 找到 {len(search_ids2)} 个 - IDs: {search_ids2}")
        
        if doc2['id'] in search_ids2 and doc1['id'] not in search_ids2:
             print("✅ KB_Beta 搜索隔离测试通过")
        else:
             print(f"❌ KB_Beta 搜索隔离失败")

        # 清理数据
        print("\n--- 清理测试数据 ---")
        await ds.delete_document(doc1['id'], user.id)
        await ds.delete_document(doc2['id'], user.id)
        await ks.delete_knowledge_base(kb1.id)
        await ks.delete_knowledge_base(kb2.id)
        await db.delete(user)
        await db.commit()
        print("清理完成")

if __name__ == "__main__":
    asyncio.run(test_isolation())
