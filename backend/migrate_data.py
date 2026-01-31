
import asyncio
import sqlite3
import asyncpg
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
SQLITE_DB = os.getenv("SQLITE_DB_PATH", "./backend/data/office_assistant.db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "office_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "office_password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "office_assistant")

async def migrate():
    print(f"🚀 开始从 SQLite ({SQLITE_DB}) 迁移数据到 PostgreSQL ({POSTGRES_HOST})...")
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ 错误: 找不到 SQLite 数据库文件 {SQLITE_DB}")
        return

    # 连接 SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # 连接 PostgreSQL
    try:
        pg_conn = await asyncpg.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB
        )
    except Exception as e:
        print(f"❌ 无法连接到 PostgreSQL: {e}")
        print("提示: 请确保 Docker 容器已启动并在运行。")
        return

    try:
        # 获取所有表
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in sqlite_cursor.fetchall() if not row['name'].startswith('sqlite_')]

        for table in tables:
            print(f"正在迁移表: {table}...")
            
            # 读取 SQLite 数据
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  - 表 {table} 为空，跳过。")
                continue

            # 获取列名
            columns = rows[0].keys()
            col_names = ", ".join(columns)
            placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])
            
            # 写入 PostgreSQL
            # 注意: 某些字段类型可能需要转换，这里做简单映射
            insert_sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            count = 0
            for row in rows:
                values = [dict(row)[col] for col in columns]
                # 简单转换: SQLite 没有原生的 UUID 或 JSONB，通常存为字符串
                await pg_conn.execute(insert_sql, *values)
                count += 1
            
            print(f"  ✅ 成功迁移 {count} 条记录到 {table}")

    finally:
        sqlite_conn.close()
        await pg_conn.close()
        print("\n🎉 迁移完成！")

if __name__ == "__main__":
    asyncio.run(migrate())
