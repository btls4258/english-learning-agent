#/home/btls/english-learning-agent/backend/.env
import asyncio
from logging.config import fileConfig
import os
import sys

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ----------------------------------------------------------------------
# 1. 关键修改：让 Alembic 能找到我们的 app 文件夹
# ----------------------------------------------------------------------
sys.path.append(os.getcwd())

# ----------------------------------------------------------------------
# 2. 关键修改：加载环境变量 (.env)
# ----------------------------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

# ----------------------------------------------------------------------
# 3. 关键修改：导入我们的 Base，这样 Alembic 才能监控模型变化
# ----------------------------------------------------------------------
from app.database import Base
from app import models
# 获取 Alembic 配置对象
config = context.config

# ----------------------------------------------------------------------
# 4. 关键修改：用 .env 里的 DATABASE_URL 覆盖 alembic.ini 里的配置
# ----------------------------------------------------------------------
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------------------------------------
# 5. 关键修改：绑定元数据
# ----------------------------------------------------------------------
target_metadata = Base.metadata

# 其他配置项
# ...

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行具体的迁移操作"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """运行异步迁移的核心逻辑"""
    
    # 创建异步引擎
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 建立连接并运行同步的迁移函数
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # 启动异步运行
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()