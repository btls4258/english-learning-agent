# 英语学习Agent使用指南

## 🎯 项目概述

这是一个基于LangChain v1.0架构的智能英语学习Agent，名为Emma。Emma具备专业的教学能力和丰富的学习工具。

## 🚀 快速开始

### 1. 测试Agent功能
```bash
python test_agent_simple.py
```

### 2. 启动后端服务
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 3. 启动前端应用
```bash
cd frontend
flutter run
```

## 🤖 Agent功能特性

### 核心能力
- **智能对话**: Emma可以像真正的英语老师一样与学生对话
- **工具调用**: 具备9个专业学习工具，支持复杂教学场景
- **个性化教学**: 根据学生水平调整教学内容和难度
- **上下文记忆**: 保持对话连续性，理解学习进度

### 学习工具
1. **字典查询** - 智能查询单词含义、发音和用法
2. **词汇练习** - 动态生成各种主题的词汇练习题
3. **语法解释** - 详细解释语法点和用法规则
4. **学习进度** - 跟踪学习进度和掌握情况
5. **复习推荐** - 智能推荐需要复习的单词
6. **学习记录** - 记录学习成果和下次复习时间
7. **发音指导** - 提供单词发音要点和相似音对比
8. **对话练习** - 创建各种场景的对话练习
9. **批量查词** - 一次性查询多个单词的含义

## 💬 使用示例

### 基础对话
- "Hello Emma, how are you?"
- "Can you help me with English?"
- "What's the weather like?"

### 学习功能
- **查单词**: "Please search the word 'accomplish'"
- **语法**: "Explain present tense grammar"
- **练习**: "Create a vocabulary exercise about animals"
- **进度**: "Check my learning progress"
- **复习**: "What words do I need to review today?"

### 高级功能
- **个性化**: "I'm intermediate level, focus on business English"
- **场景练习**: "Create a restaurant conversation practice"
- **发音帮助**: "How do I pronounce 'world' correctly?"

## 🏗️ 技术架构

### LangChain v1.0兼容
- 使用`create_agent()`标准模式
- 支持`@tool`装饰器工具
- 实现ReAct推理-行动循环
- 集成ToolNode工具编排

### 核心组件
- `EnglishLearningAgent`: 主要Agent类
- `AgentManager`: 多用户Agent管理
- `LearningTools`: 9个专业学习工具
- `LLMProviders`: DeepSeek和GLM4支持

### 数据库集成
- SQLAlchemy异步ORM
- 用户学习记录存储
- SM-2记忆算法支持
- 进度跟踪系统

## 🔧 配置说明

### 环境变量
```bash
DEEPSEEK_API_KEY=your_deepseek_key
GLM4_API_KEY=your_glm4_key
GLM4_API_BASE=your_glm4_endpoint
DEFAULT_LLM_PROVIDER=deepseek
```

### Agent设置
```python
# 创建Agent
agent = EnglishLearningAgent(
    provider="deepseek",
    user_context={
        "level": "intermediate",
        "goals": ["conversation", "business"]
    }
)

# 设置数据库上下文
agent.set_learning_context(db_session, user_id)
```

## 📱 API接口

### 主要端点
- `POST /chat/` - 发送消息给Emma
- `GET /chat/history` - 获取对话历史
- `POST /chat/clear` - 清空对话历史
- `GET /chat/agent-info` - 获取Agent信息
- `POST /chat/update-context` - 更新用户上下文
- `GET /chat/tools` - 获取可用工具列表

### 请求示例
```json
POST /chat/
{
  "message": "Please help me learn business vocabulary",
  "provider": "deepseek",
  "user_context": {
    "level": "intermediate",
    "goals": ["business", "writing"]
  }
}
```

### 响应示例
```json
{
  "response": "I'll help you learn business vocabulary! Let's start with...",
  "provider": "deepseek",
  "tools_used": ["create_vocabulary_exercise", "search_dictionary"],
  "session_info": {
    "conversation_length": 5,
    "tools_available": 9
  }
}
```

## 🧪 测试和调试

### 运行测试
```bash
# 基础功能测试
python test_agent_simple.py

# 详细测试
cd backend
python -m pytest tests/ -v
```

### 常见问题
1. **API Key未设置**: 检查`.env`文件中的API密钥配置
2. **数据库连接失败**: 确保数据库服务正常运行
3. **工具调用失败**: 检查数据库上下文是否正确设置

## 📈 性能优化

### Agent管理
- 使用`AgentManager`管理多用户实例
- 自动清理不活跃的Agent
- 支持用户级别的配置缓存

### 工具优化
- 异步数据库操作
- 结果缓存机制
- 错误处理和重试

## 🔮 未来功能

### 计划中的特性
- 语音识别和发音评测
- 图片内容理解和描述
- 多语言翻译支持
- 学习数据分析和报表
- 社交学习功能
- 游戏化学习体验

### 扩展点
- 新的学习工具开发
- 更多LLM提供商支持
- 自定义教学内容模板
- 第三方教育平台集成

## 💡 最佳实践

### 教学建议
- 根据学生水平调整难度
- 提供具体实用的例子
- 鼓励学生多练习口语
- 定期复习和巩固

### 开发建议
- 遵循LangChain v1.0规范
- 实现完整的错误处理
- 添加详细的日志记录
- 进行充分的测试验证

---

**🎉 开始你的智能英语学习之旅吧！Emma随时准备帮助你提升英语水平！**