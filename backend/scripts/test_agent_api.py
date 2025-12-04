#!/usr/bin/env python3
"""
Agent API 测试脚本（Python版本）
更详细的测试，包含错误处理
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_step(step_num: int, description: str):
    """打印测试步骤"""
    print(f"\n{Colors.YELLOW}{'='*50}")
    print(f"步骤 {step_num}: {description}")
    print(f"{'='*50}{Colors.NC}\n")

def print_success(message: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")

def print_info(message: str):
    """打印信息消息"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.NC}")

def register_user(email: str, username: str, password: str) -> bool:
    """注册用户"""
    print_step(1, "注册用户")
    try:
        response = requests.post(
            f"{BASE_URL}/users/",
            json={
                "email": email,
                "username": username,
                "password": password
            }
        )
        if response.status_code == 200:
            print_success("用户注册成功")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return True
        elif response.status_code == 400:
            print_info("用户已存在，跳过注册")
            return True
        else:
            print_error(f"注册失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"注册异常: {str(e)}")
        return False

def login(email: str, password: str) -> Optional[str]:
    """登录获取Token"""
    print_step(2, "登录获取Token")
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": email,
                "password": password
            }
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success("登录成功")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print_error(f"登录失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"登录异常: {str(e)}")
        return None

def chat(token: str, message: str, provider: Optional[str] = None, clear_history: bool = False) -> Optional[dict]:
    """发送对话请求"""
    try:
        payload = {
            "message": message,
            "clear_history": clear_history
        }
        if provider:
            payload["provider"] = provider
        
        response = requests.post(
            f"{BASE_URL}/chat/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"对话请求失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"对话异常: {str(e)}")
        return None

def get_history(token: str) -> Optional[list]:
    """获取对话历史"""
    try:
        response = requests.get(
            f"{BASE_URL}/chat/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"获取历史失败: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"获取历史异常: {str(e)}")
        return None

def clear_history(token: str) -> bool:
    """清空对话历史"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/clear",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return True
        else:
            print_error(f"清空历史失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"清空历史异常: {str(e)}")
        return False

def main():
    """主测试流程"""
    print(f"{Colors.BLUE}{'='*50}")
    print("Agent API 测试脚本 (Python版本)")
    print(f"{'='*50}{Colors.NC}")
    
    # 测试用户信息
    email = "test@example.com"
    username = "testuser"
    password = "testpass123"
    
    # 1. 注册用户
    if not register_user(email, username, password):
        print_error("注册失败，退出测试")
        return
    
    # 2. 登录
    token = login(email, password)
    if not token:
        print_error("登录失败，退出测试")
        return
    
    # 3. 第一轮对话
    print_step(3, "第一轮对话 - 英语自我介绍")
    response1 = chat(token, "你好，请用英语简单介绍一下自己", provider="deepseek")
    if response1:
        print_success("对话成功")
        print(json.dumps(response1, indent=2, ensure_ascii=False))
        print_info(f"使用的Provider: {response1.get('provider')}")
    
    # 4. 第二轮对话（测试上下文）
    print_step(4, "第二轮对话 - 测试上下文记忆")
    response2 = chat(token, "我刚才说了什么？请用英语回答")
    if response2:
        print_success("对话成功")
        print(json.dumps(response2, indent=2, ensure_ascii=False))
    
    # 5. 获取对话历史
    print_step(5, "获取对话历史")
    history = get_history(token)
    if history is not None:
        print_success(f"获取到 {len(history)} 条历史记录")
        for i, msg in enumerate(history, 1):
            msg_type = msg.get("type", "unknown")
            content = msg.get("content", "")[:100]  # 只显示前100个字符
            print(f"  {i}. [{msg_type}]: {content}...")
    
    # 6. 清空历史
    print_step(6, "清空对话历史")
    if clear_history(token):
        print_success("历史已清空")
    
    # 7. 验证历史已清空
    print_step(7, "验证历史已清空")
    history_after = get_history(token)
    if history_after == []:
        print_success("历史已成功清空")
    else:
        print_error(f"历史未清空，仍有 {len(history_after)} 条记录")
    
    # 8. 测试新对话（清空后）
    print_step(8, "清空后的新对话")
    response3 = chat(token, "Hello, what's your name?", clear_history=False)
    if response3:
        print_success("对话成功")
        print(json.dumps(response3, indent=2, ensure_ascii=False))
    
    print(f"\n{Colors.GREEN}{'='*50}")
    print("测试完成！")
    print(f"{'='*50}{Colors.NC}\n")

if __name__ == "__main__":
    main()

