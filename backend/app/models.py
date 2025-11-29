from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    # --- User 表保持不变 ---
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


# --- 新增的部分 ---

class Book(Base):
    """
    单词书/考纲表
    例如：id=1, title="考研英语大纲词汇", code="kaoyan"
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False) # 书名
    code = Column(String, unique=True, index=True, nullable=False) # 代号，比如 'cet4', 'kaoyan'
    description = Column(String, nullable=True) # 描述
    
    # 关系：一本书包含多个单词
    # back_populates 指向 Word 类里的 'book' 属性
    # cascade="all, delete-orphan" 表示如果删除书，属于这本书的单词也会被自动删除，防止产生垃圾数据
    words = relationship("Word", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book(title='{self.title}', code='{self.code}')>"


class Word(Base):
    """
    单词表
    """
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    spelling = Column(String, index=True, nullable=False) # 单词拼写，如 'abandon'
    phonetic = Column(String, nullable=True) # 音标
    
    # 释义我们暂时用简单字符串存，未来可以用 JSON 存复杂的词性变化
    meaning = Column(Text, nullable=False)   # 中文释义
    
    # --- 外键关联 ---
    # ForeignKey("books.id") 里的 books 是表名，不是类名
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    # 关系：一个单词属于一本书
    book = relationship("Book", back_populates="words")

    def __repr__(self):
        return f"<Word(spelling='{self.spelling}', book_id={self.book_id})>"

class UserWordProgress(Base):
    """
    用户单词学习进度表
    记录：哪个用户(user_id)，学了哪个词(word_id)，学得怎样(proficiency)
    """
    __tablename__ = "user_word_progress"

    id = Column(Integer, primary_key=True, index=True)
    
    # 1. 核心关联：谁学的？学的哪个词？
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    
    # 2. 记忆算法核心字段 (为艾宾浩斯/SM-2算法做准备)
    is_mastered = Column(Boolean, default=False)  # 是否已完全掌握（斩词）
    proficiency = Column(Integer, default=0)      # 熟练度 (0-5)，类似 Anki 的打分
    
    # 3. 时间字段 (调度复习的关键)
    next_review_at = Column(DateTime(timezone=True), nullable=True) # 下次该复习的时间
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True) # 上次复习时间
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # 4. 建立反向关系 (可选，方便查询)
    # 这样 user.progresses 就能拿到该用户所有的学习记录
    # word.progresses 就能拿到这个词被哪些用户学过
    user = relationship("User", backref="progresses") 
    word = relationship("Word", backref="progresses")

    # 5. 关键约束：一个用户对同一个单词，只能有一条记录！
    # 这是一个数据库层面的“保险锁”
    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='uix_user_word'),
    )

    def __repr__(self):
        return f"<Progress(user={self.user_id}, word={self.word_id}, prof={self.proficiency})>"