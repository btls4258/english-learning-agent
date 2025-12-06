# English Learning Agent 测试

简单的API测试，验证主要功能是否正常工作。

## 📁 测试文件结构

```
backend/tests/
├── conftest.py              # pytest配置和测试数据
├── test_main_apis.py        # 主要API端点测试
├── test_study.py            # 学习功能测试
├── test_chat_agent.py       # 聊天Agent测试
└── README.md               # 测试说明
```

## 🎯 测试覆盖范围

### 核心API测试 (test_main_apis.py)
- 健康检查
- 用户注册/登录
- 学习进度管理
- 聊天功能
- 权限验证

### 学习功能测试 (test_study.py)
- SM-2算法验证
- 完整学习流程
- 复习逻辑测试

### 聊天功能测试 (test_chat_agent.py)
- Agent初始化
- 单轮/多轮对话
- 历史记录管理

## 🚀 运行测试

```bash
# 运行所有测试
pytest backend/tests/

# 运行特定测试文件
pytest backend/tests/test_main_apis.py

# 显示详细输出
pytest backend/tests/ -v

# 生成覆盖率报告
pytest backend/tests/ --cov=app

# 运行特定测试
pytest backend/tests/test_study.py::test_full_learning_flow -v
```

## 📝 测试特点

- **简单实用**：专注于验证功能是否正常工作
- **快速执行**：使用内存数据库，避免外部依赖
- **独立运行**：每个测试都是独立的，可以单独运行
- **清晰输出**：测试结果直观易懂

## 🔧 环境要求

- Python 3.8+
- pytest
- aiosqlite (用于内存数据库测试)
- httpx (用于异步HTTP测试)