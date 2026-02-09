
import asyncio
import sys
import os
from sqlalchemy import select

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import async_session, init_db
from app.models.user import User
from app.services.knowledge_service import KnowledgeService
from app.services.document_service import DocumentService
from fastapi import UploadFile
from io import BytesIO

async def test_knowledge_system():
    print("=== 开始测试知识库系统 ===")
    
    # 初始化数据库
    await init_db()
    
    async with async_session() as db:
        # 1. 获取或创建测试用户
        query = select(User).where(User.username == "test_user")
        result = await db.execute(query)
        user = result.scalars().first()
        if not user:
            user = User(username="test_user", email="test@example.com", hashed_password="hashed_password")
            db.add(user)
            await db.commit()
            await db.refresh(user)
        print(f"测试用户 ID: {user.id}")
        
        # 2. 创建知识库
        ks = KnowledgeService(db)
        kb = await ks.create_knowledge_base("我的产品文档", user.id, "存放产品相关资料")
        print(f"知识库创建成功: {kb.name} (ID: {kb.id})")
        
        # 3. 创建目录
        root_tree = await ks.get_directory_tree(kb.id)
        root_dir_id = root_tree[0]['id'] # 根目录
        
        dir1 = await ks.create_directory("技术规范", kb.id, root_dir_id)
        dir2 = await ks.create_directory("API 文档", kb.id, dir1.id)
        print(f"目录结构创建成功: 根 -> {dir1.name} -> {dir2.name}")
        
        # 4. 创建标签
        tag1 = await ks.create_tag("重要")
        tag2 = await ks.create_tag("v1.0")
        print(f"标签创建成功: {tag1.name}, {tag2.name}")
        
        # 5. 上传文档 (模拟)
        ds = DocumentService(db)
        file_content = b"# API Documentation\n\nThis is a test document."
        file = UploadFile(filename="api_v1.md", file=BytesIO(file_content))
        
        # 注意：这里会尝试连接 ES，如果 ES 没启动会报错，我们捕获一下
        try:
            doc_result = await ds.create_document(
                title="API V1 接口文档", 
                file=file, 
                user_id=user.id, 
                kb_id=kb.id, 
                dir_id=dir2.id
            )
            print(f"文档创建成功: {doc_result['title']} (ID: {doc_result['id']})")
            
            # 6. 添加标签
            await ks.add_tags_to_document(doc_result['id'], ["重要", "v1.0"])
            print("标签关联成功")
            
            # 7. 更新文档 (触发版本控制)
            update_data = {
                "content": "# API Documentation V1.1\n\nUpdated content.",
                "change_log": "修正了一些错误"
            }
            updated_doc = await ds.update_document(doc_result['id'], update_data, user.id)
            print(f"文档更新成功，当前版本: {updated_doc.get('current_version', 'Unknown')}")
            
        except Exception as e:
            print(f"文档操作出错 (可能是 ES 未连接): {e}")

    print("=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_knowledge_system())
