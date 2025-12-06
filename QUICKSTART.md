# 快速启动指南

## 前后端连接已完成 ✅

项目已完成前后端连接，包括：
- ✅ 后端CORS配置
- ✅ 前端API服务层
- ✅ 登录/注册页面
- ✅ 聊天界面连接后端
- ✅ Token认证机制

## 快速启动步骤

### 1. 启动后端（WSL2）

```bash
cd ~/english-learning-agent/backend
source venv/bin/activate  # 如果使用venv
uvicorn app.main:app --reload --host 0.0.0.0
```

后端将在 `http://0.0.0.0:8000` 运行

### 2. 获取WSL2 IP地址（如果需要）

如果Windows无法访问 `localhost:8000`，运行：

```bash
hostname -I
```

会显示类似：`172.20.10.2`

### 3. 配置前端API地址

编辑 `frontend/lib/services/api_service.dart`：

如果Windows可以直接访问 `localhost:8000`，保持：
```dart
static const String baseUrl = 'http://localhost:8000';
```

如果不行，改为WSL2的IP：
```dart
static const String baseUrl = 'http://172.20.10.2:8000';  // 替换为你的IP
```

### 4. 安装前端依赖（Windows PowerShell）

```bash
cd frontend
flutter pub get
```

### 5. 运行前端

```bash
flutter run
```

或使用VS Code/Android Studio运行

## 测试连接

### 方法1: 使用Python测试脚本（推荐）

```bash
# 在WSL2中
cd ~/english-learning-agent
python3 test_api.py
```

### 方法2: 使用Bash测试脚本

```bash
# 在WSL2中
cd ~/english-learning-agent
./test_api.sh
```

### 方法3: 手动测试

1. **健康检查**
   ```bash
   curl http://localhost:8000/health
   ```

2. **注册用户**
   ```bash
   curl -X POST http://localhost:8000/users/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","username":"testuser","password":"test123456"}'
   ```

3. **登录获取Token**
   ```bash
   curl -X POST http://localhost:8000/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=test123456"
   ```

## 使用应用

1. **首次使用**
   - 打开应用，看到登录页面
   - 点击"还没有账户？点击注册"
   - 输入邮箱、用户名、密码（至少6位）
   - 点击"注册"，自动跳转到聊天页面

2. **登录**
   - 在登录页面输入已注册的邮箱和密码
   - 点击"登录"

3. **聊天**
   - 在聊天页面输入消息
   - 点击发送按钮或按Enter
   - AI会回复你的消息

4. **登出**
   - 点击右上角登出按钮
   - 返回登录页面

## 常见问题

### Q: 前端显示"网络错误"
**A:** 
1. 确认后端正在运行
2. 检查 `api_service.dart` 中的 `baseUrl` 是否正确
3. 如果使用WSL2，尝试使用WSL2的IP而不是localhost

### Q: 无法访问 localhost:8000
**A:** 
1. 在WSL2中运行 `hostname -I` 获取IP
2. 修改前端 `api_service.dart` 中的 `baseUrl` 为WSL2 IP

### Q: CORS错误
**A:** 
1. 确认后端已添加CORS中间件（检查 `main.py`）
2. 重启后端服务

### Q: 401 Unauthorized
**A:** 
1. 确认已登录（token已保存）
2. 尝试重新登录

## 项目结构

```
english-learning-agent/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI主文件（已添加CORS）
│       ├── api/
│       │   └── chat.py          # 聊天API
│       └── agents/
│           └── chat_agent.py    # ChatAgent实现
├── frontend/
│   └── lib/
│       ├── main.dart            # 主入口（已更新）
│       ├── services/
│       │   └── api_service.dart # API服务层（新建）
│       └── screens/
│           ├── login_screen.dart # 登录/注册页面（新建）
│           └── chat_screen.dart  # 聊天页面（新建）
├── test_api.py                  # Python测试脚本（新建）
├── test_api.sh                  # Bash测试脚本（新建）
├── TESTING.md                   # 详细测试文档（新建）
└── QUICKSTART.md               # 本文件
```

## 下一步开发

完成前后端连接后，可以继续实现：

1. **单词学习功能**
   - 设置学习计划
   - 显示需要复习的单词
   - 显示新学的单词

2. **学习进度跟踪**
   - 将学习进度作为上下文传入大模型
   - 实现记忆曲线算法

3. **升级LangChain Agent**
   - 使用LangChain v1.0推荐的agent实现方式
   - 添加工具（tools）支持

4. **更多题型**
   - 词义辨析
   - 挖空拼写
   - 完整单词拼写
   - 听写等

## 技术支持

如有问题，请查看：
- `TESTING.md` - 详细测试文档
- 后端日志 - 查看错误信息
- Flutter调试控制台 - 查看前端错误

