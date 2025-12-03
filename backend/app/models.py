#/home/btls/english-learning-agent/backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Float
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

# /home/btls/english-learning-agent/backend/app/models.py
# ... (前面的 User, Book, Word 保持不变，不要动)

class UserWordProgress(Base):
    """
    用户单词学习进度表 (升级版：支持 SM-2 算法)
    """
    __tablename__ = "user_word_progress"

    id = Column(Integer, primary_key=True, index=True)
    
    # 关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    
    # --- 学习状态 ---
    is_mastered = Column(Boolean, default=False)  # 是否已斩词

    # --- SM-2 算法核心参数 (NEW) ---
    # 1. 易记因子 (Easiness Factor)，标准初始值为 2.5
    easiness_factor = Column(Float, default=2.5) 
    # 2. 下次复习间隔 (Interval)，单位：天
    interval = Column(Integer, default=0)
    # 3. 连续正确次数 (Repetitions)
    repetitions = Column(Integer, default=0)

    # --- 时间字段 ---
    next_review_at = Column(DateTime(timezone=True), nullable=True) # 下次复习的具体日期
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # 关系和约束
    user = relationship("User", backref="progresses") 
    word = relationship("Word", backref="progresses")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='uix_user_word'),
    )
    
    # 删掉了之前的 proficiency，因为 repetitions 可以替代它，或者你可以保留它作为辅助显示
    # 为了防止报错，如果你想保留 proficiency 也可以，但 SM-2 主要靠上面三个参数。
    # 这里我们选择保留 proficiency 作为一个简单的 0-100 的直观展示分数，不参与核心算法
    proficiency = Column(Integer, default=0) 

    def __repr__(self):
        return f"<Progress(u={self.user_id}, w={self.word_id}, interval={self.interval}d)>"