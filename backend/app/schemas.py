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

    class Config:
        from_attributes = True