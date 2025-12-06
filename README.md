# English Learning Agent - AI-Powered English Exam Preparation System

<p align="center">
  <strong>基于大模型的个性化英语备考智能助教系统</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1.0-4A90E2?style=for-the-badge&logo=python&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
</p>

## 📖 项目简介

English Learning Agent 是一个智能化的英语备考学习系统，专门帮助中国用户准备各类英语考试。系统结合了大语言模型能力和个性化学习算法，提供自适应的交互式学习体验。

### 🎯 支持的考试类型
- **研究生入学考试 (考研)** - 完整功能支持
- **大学英语四级 (CET-4)** - 开发中
- **大学英语六级 (CET-6)** - 开发中
- **高考英语** - 开发中

### 🚀 核心特色
- **AI智能助教 Emma** - 专业的英语学习助手，提供个性化指导
- **对话式学习界面** - 类似ChatGPT的自然交互体验
- **智能词汇学习** - 基于艾宾浩斯遗忘曲线的记忆算法
- **自适应学习路径** - 根据用户水平动态调整学习内容

## ✨ 主要功能

### 🔐 用户系统
- [x] 用户注册和登录
- [x] JWT token认证
- [x] 个人学习偏好设置

### 📚 智能学习界面
- [x] **聊天式交互界面** - 现代化的对话学习体验
- [x] **智能按钮导航** - 快速访问各种学习功能
- [x] **多考试方向支持** - 一键切换备考目标
- [x] **设置管理中心** - 右上角设置，管理学习偏好

### 📖 词汇学习系统
- [x] **背单词界面** - 完整的UI交互框架
- [x] **复习单词** - 智能复习计划 (UI完成，后端开发中)
- [x] **新单词学习** - 个性化新词推荐 (UI完成，后端开发中)
- [x] **进度评估** - 学习数据分析 (UI完成，后端开发中)
- [ ] **记忆曲线算法** - SM-2间隔重复算法
- [ ] **学习数据持久化** - 用户进度和错题记录

### 🎯 其他学习模块 (开发中)
- [ ] 真题练习 - 历年真题训练
- [ ] 模拟考试 - 全真模拟测试
- [ ] 听力训练 - 听力理解练习
- [ ] 口语练习 - 口语表达能力提升

## 🏗️ 技术架构

### 后端架构
```
Backend (FastAPI + LangChain v1.0)
├── 🤖 AI Agent System
│   ├── Emma - 英语学习AI助教
│   ├── 9个专业学习工具
│   └── DeepSeek/GLM4 LLM支持
├── 📊 数据存储
│   ├── PostgreSQL (主数据库)
│   ├── SQLAlchemy ORM (异步)
│   └── SM-2记忆算法实现
├── 🔐 认证系统
│   ├── JWT token认证
│   └── 密码安全存储
└── 🧪 测试覆盖
    └── 30个测试用例，100%通过率
```

### 前端架构
```
Frontend (Flutter + Material Design)
├── 📱 用户界面
│   ├── 登录注册界面
│   ├── 主聊天界面
│   └── 设置管理界面
├── 🎨 交互设计
│   ├── 智能按钮系统
│   ├── 动态界面更新
│   └── 响应式布局
└── 🔌 API集成
    ├── RESTful API通信
    └── 实时状态管理
```

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Flutter SDK 3.0+
- PostgreSQL 12+
- Git

### 1. 克隆项目
```bash
git clone https://github.com/your-username/english-learning-agent.git
cd english-learning-agent
```

### 2. 后端设置
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置API密钥和数据库配置

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
flutter pub get

# 运行应用
flutter run
```

### 4. 访问应用
- **前端应用**: http://localhost:3000 (或Flutter设备地址)
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🧪 测试

### 运行后端测试
```bash
cd backend
./run_tests.sh
# 或
pytest tests/ -v
```

### 运行前端测试
```bash
cd frontend
flutter test
```

## 📊 项目状态

### ✅ 已完成功能
- [x] **完整的认证系统** - 用户注册、登录、JWT认证
- [x] **AI Agent框架** - LangChain v1.0架构，9个学习工具配置
- [x] **现代化UI界面** - 聊天式学习界面，智能按钮导航
- [x] **数据库架构** - PostgreSQL + SQLAlchemy异步ORM
- [x] **测试覆盖** - 30个测试用例，100%通过率
- [x] **跨平台支持** - Flutter支持Web、移动端、桌面端

### 🔄 当前开发重点
- [ ] **激活Agent工具调用** - 让Emma真正使用学习工具
- [ ] **实现学习数据存储** - 用户进度、词汇掌握情况等
- [ ] **词汇学习后端** - 真正的复习、新词、进度评估功能
- [ ] **数据库集成** - 连接UI操作到实际学习功能

### 📋 开发路线图

#### Phase 1: 核心词汇学习 (当前)
- [x] 前端UI框架
- [ ] 工具调用激活
- [ ] 学习数据存储
- [ ] 词汇学习功能实现

#### Phase 2: 完善学习系统
- [ ] 真题练习功能
- [ ] 错题本分析
- [ ] 学习报告生成
- [ ] 其他考试方向支持

#### Phase 3: 高级功能
- [ ] 听力训练模块
- [ ] 口语练习功能
- [ ] 学习社交功能
- [ ] 移动端优化

## 📚 API文档

### 主要接口

#### 认证相关
```
POST /users/     # 用户注册
POST /token/     # 用户登录
```

#### 聊天和Agent
```
POST /chat/              # 与AI助教对话
GET  /chat/history       # 获取聊天历史
POST /chat/clear         # 清空聊天记录
GET  /chat/agent-info    # 获取Agent信息
```

#### 学习功能
```
POST /study/progress     # 创建学习记录
GET  /study/needs-review # 获取复习单词
POST /study/review       # 更新学习进度
```

完整的API文档请访问: http://localhost:8000/docs

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循 PEP 8 Python代码规范
- 使用有效的Dart/Flutter约定
- 确保所有测试通过
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [详细文档](./claude.md) - 完整的技术文档
- [Agent使用指南](./AGENT_GUIDE.md) - AI助教使用说明
- [快速开始指南](./QUICKSTART.md) - 详细的设置指南
- [更新日志](./CHANGELOG.md) - 版本更新历史

## 📞 联系我们

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 技术讨论: [Discussions]

---

<p align="center">
  <strong>让AI助教Emma帮助你高效备考英语！🚀</strong>
</p>

**最后更新**: 2025年12月6日
**版本**: 1.0.0-alpha
**状态**: 活跃开发中 (前端完成，后端工具开发中)