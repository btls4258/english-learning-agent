#!/usr/bin/env python3
"""
检查并清理无效用户（密码哈希格式不正确的用户）
"""
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.database import get_db
from app.models import User
from sqlalchemy import select

async def check_and_cleanup():
    async for db in get_db():
        stmt = select(User)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        print(f"数据库中共有 {len(users)} 个用户\n")
        print("=" * 60)
        
        valid_users = []
        invalid_users = []
        
        for user in users:
            # 检查是否是有效的bcrypt哈希
            is_valid_bcrypt = (
                user.hashed_password and 
                user.hashed_password.startswith("$2b$") and
                len(user.hashed_password) >= 60
            )
            
            print(f"\n用户ID: {user.id}")
            print(f"邮箱: {user.email}")
            print(f"用户名: {user.username}")
            
            if is_valid_bcrypt:
                print("✓ 密码哈希格式正确（bcrypt）")
                valid_users.append(user)
            else:
                print("✗ 密码哈希格式不正确")
                print(f"  当前哈希: {user.hashed_password}")
                invalid_users.append(user)
            
            print("-" * 60)
        
        print(f"\n总结:")
        print(f"  有效用户: {len(valid_users)}")
        print(f"  无效用户: {len(invalid_users)}")
        
        if invalid_users:
            print(f"\n⚠️  发现 {len(invalid_users)} 个无效用户:")
            for user in invalid_users:
                print(f"    - {user.email} (ID: {user.id})")
            
            # 询问是否删除
            print(f"\n准备删除这 {len(invalid_users)} 个无效用户...")
            
            for user in invalid_users:
                await db.delete(user)
                print(f"  ✓ 已删除: {user.email}")
            
            await db.commit()
            print(f"\n✅ 已删除 {len(invalid_users)} 个无效用户")
        else:
            print("\n✅ 所有用户的密码哈希格式都正确！")
        
        break

if __name__ == "__main__":
    asyncio.run(check_and_cleanup())

