# /home/btls/english-learning-agent/backend/init_data.py
import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models import Book, Word

# --- 模拟数据源 ---
BOOKS_DATA = [
    {"title": "考研英语大纲词汇", "code": "kaoyan", "desc": "2025考研必背"},
    {"title": "CET-4 大学英语四级", "code": "cet4", "desc": "大学英语四级核心词汇"},
]

# 50个考研/四级高频词 (节选)
WORDS_DATA = [
    ("abandon", "v. 放弃，遗弃；n. 放任，狂热"),
    ("abide", "v. 容忍，忍受；遵守，忠于"),
    ("ability", "n. 能力；本领；才能"),
    ("abolish", "v. 废除，取消"),
    ("abrupt", "adj. 突然的，意外的；唐突的"),
    ("absence", "n. 缺席，不在；缺乏，没有"),
    ("absorb", "v. 吸收；同化；吸引…的注意"),
    ("abstract", "adj. 抽象的 n. 摘要 v. 提取"),
    ("absurd", "adj. 荒谬的，可笑的"),
    ("abundance", "n. 丰富，充裕"),
    ("abuse", "v./n. 滥用；虐待；谩骂"),
    ("academy", "n. 研究院；学会；专门学校"),
    ("accelerate", "v. 加速；促进"),
    ("access", "n. 进入；入口；接近的机会 v. 存取"),
    ("accessible", "adj. 易接近的；可到达的；可理解的"),
    ("accommodate", "v. 容纳；向…提供住处；适应"),
    ("company", "n. 公司；陪伴；连队"),
    ("accompany", "v. 陪伴；伴随；伴奏"),
    ("accomplish", "v. 完成，实现"),
    ("accord", "v./n. 一致；符合；协议"),
    ("account", "n. 账户；解释；账目 v. 说明"),
    ("accumulate", "v. 积累，堆积"),
    ("accurate", "adj. 准确的，精确的"),
    ("accuse", "v. 指责，控告"),
    ("accustom", "v. 使习惯于"),
    ("achieve", "v. 实现，完成；达到"),
    ("acknowledge", "v. 承认；致谢；告知收到"),
    ("acquire", "v. 获得；学到"),
    ("acquisition", "n. 获得；获得物"),
    ("acre", "n. 英亩"),
    ("action", "n. 行动；作用；情节"),
    ("activate", "v. 激活；使活动"),
    ("acute", "adj. 严重的；敏锐的；急性的"),
    ("adapt", "v. 使适应；改编"),
    ("addict", "v. 使沉溺；使上瘾 n. 入迷的人"),
    ("addition", "n. 增加；加法"),
    ("additional", "adj. 附加的，额外的"),
    ("address", "n. 地址；演说 v. 处理；致辞"),
    ("adequate", "adj. 足够的；合格的"),
    ("adhere", "v. 黏附；坚持；遵守"),
    ("adjacent", "adj. 邻近的，毗连的"),
    ("adjust", "v. 调整，调节；适应"),
    ("administer", "v. 管理；执行；给予"),
    ("administration", "n. 管理；行政；政府"),
    ("admire", "v. 钦佩；赞美"),
    ("admission", "n. 准许进入；承认；入场费"),
    ("admit", "v. 承认；准许进入"),
    ("adolescent", "n. 青少年 adj. 青春期的"),
    ("adopt", "v. 采用；收养"),
    ("advance", "v./n. 前进；推进；提前"),
]

async def init_db_data():
    print("🚀 开始初始化更丰富的数据...")
    
    async with SessionLocal() as db:
        # 1. 初始化书籍
        books_map = {} 
        
        for b_data in BOOKS_DATA:
            result = await db.execute(select(Book).where(Book.code == b_data["code"]))
            book = result.scalar_one_or_none()
            
            if not book:
                print(f"➕ 创建书籍: {b_data['title']}")
                book = Book(title=b_data["title"], code=b_data["code"], description=b_data["desc"])
                db.add(book)
            else:
                print(f"✅ 书籍已存在: {b_data['title']}")
            
            books_map[b_data["code"]] = book

        # 【关键修改】：这里加上 flush，强制数据库生成 ID，否则后面查 Word.book == book 会报错
        await db.flush()

        # 2. 初始化单词
        kaoyan_book = books_map["kaoyan"]
        cet4_book = books_map["cet4"]
        
        count = 0
        for spelling, meaning in WORDS_DATA:
            # 查重：检查考研书里有没有这个词
            stmt = select(Word).where(Word.spelling == spelling, Word.book_id == kaoyan_book.id)
            result = await db.execute(stmt)
            existing_word = result.scalar_one_or_none()
            
            if not existing_word:
                w = Word(spelling=spelling, meaning=meaning, book=kaoyan_book)
                db.add(w)
                count += 1
            
            # 前10个词稍微改改意思加到四级里
            if count < 10:
                 stmt_cet = select(Word).where(Word.spelling == spelling, Word.book_id == cet4_book.id)
                 result_cet = await db.execute(stmt_cet)
                 if not result_cet.scalar_one_or_none():
                     w_cet = Word(spelling=spelling, meaning=meaning + " (四级释义)", book=cet4_book)
                     db.add(w_cet)

        await db.commit()
        print(f"🎉 数据初始化完成！新增了约 {count} 个单词。")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db_data())