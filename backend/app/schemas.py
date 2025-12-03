#/home/btls/english-learning-agent/backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

# 1. 基础模型：包含大家都需要的字段
class UserBase(BaseModel):
    email: EmailStr
    username: str

# 2. 注册时的模型：用户必须传密码
class UserCreate(UserBase):
    password: str

# 3. 返回给前端的模型：不能包含密码，但需要包含 id 和创建时间
class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    # 配置项：允许 Pydantic 读取 SQLAlchemy 的 ORM 模型数据
    class Config:
        from_attributes = True


# 1. 基础字段：单词进度的核心数据
class ProgressBase(BaseModel):
    word_id: int
    proficiency: int = 0  # 默认熟练度 0

# 2. 前端发来的请求数据
class ProgressCreate(ProgressBase):
    # 前端只需要传 word_id 即可，proficiency 可选
    pass

# 3. 后端返回的数据
class ProgressOut(ProgressBase):
    id: int
    user_id: int
    is_mastered: bool
    next_review_at: datetime | None  # 允许为空
    last_reviewed_at: datetime | None

    easiness_factor: float
    interval: int
    repetitions: int
    
    class Config:
        from_attributes = True

# --- 新增：用于复习列表的组合模型 ---

# 1. 先定义一个简单的单词模型，只包含我们要显示的字段
class WordSimple(BaseModel):
    id: int
    spelling: str
    meaning: str
    
    class Config:
        from_attributes = True

# 2. 定义带有单词详情的进度模型
# 继承自 ProgressOut，所以它拥有 id, next_review_at 等字段
# 但额外增加了一个 'word' 字段
class ProgressWithWord(ProgressOut):
    word: WordSimple


# --- 新增：复习打分模型 ---
class ReviewCreate(BaseModel):
    word_id: int
    quality: int  # 记忆质量打分：0=不认识, 3=模糊, 5=完全认识 (这只是个约定)

# --- 新增：Token 响应模型 ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- 新增：Token 数据模型 ---
# 用于将来解析 Token 时存储其中的信息（比如用户名）
class TokenData(BaseModel):
    email: str | None = None