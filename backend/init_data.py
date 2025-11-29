import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models import Book, Word

async def init_db_data():
    print("开始初始化数据...")
    
    # 1. 获取数据库会话
    async with SessionLocal() as db:
        
        # --- 检查是否已经存在数据（防止重复运行脚本产生重复数据）---
        result = await db.execute(select(Book).where(Book.code == "kaoyan"))
        book = result.scalar_one_or_none()
        
        if book:
            print("数据已存在，跳过初始化。")
        else:
            print("正在创建【考研英语】书籍...")
            # 2. 创建书对象
            kaoyan_book = Book(
                title="考研英语大纲词汇",
                code="kaoyan",
                description="2025年考研英语必背词汇"
            )
            
            # 3. 创建单词对象
            # 注意：我们这里直接把 单词 和 书 关联起来
            # 方法A：显式指定 book_id (需要先保存书拿到ID，比较麻烦)
            # 方法B：利用 ORM 关系，直接赋值对象 (推荐！)
            w1 = Word(spelling="abandon", meaning="v. 放弃，遗弃", book=kaoyan_book)
            w2 = Word(spelling="abide", meaning="v. 忍受；遵守", book=kaoyan_book)
            w3 = Word(spelling="ability", meaning="n. 能力，才干", book=kaoyan_book)
            
            # 4. 添加到会话
            # 只要添加了 book，因为它关联了 words，SQLAlchemy 会聪明地帮我们把关联的 words 也一起加上
            # 但为了稳妥，我们显式添加一下
            db.add(kaoyan_book)
            db.add(w1)
            db.add(w2)
            db.add(w3)
            
            # 5. 提交事务 (这一步才会真正执行 SQL 写入数据库)
            await db.commit()
            print("成功写入：1本书，3个单词！")

    # 关闭引擎连接池
    await engine.dispose()

if __name__ == "__main__":
    # 运行异步函数
    asyncio.run(init_db_data())