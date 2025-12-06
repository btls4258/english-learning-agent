#!/bin/bash

# 英语学习Agent测试脚本

echo "🧪 运行英语学习Agent测试..."
echo "=================================================="

cd backend

# 激活虚拟环境
source venv/bin/activate

# 设置Python路径
export PYTHONPATH=/home/btls/english-learning-agent/backend

# 运行测试
python tests/test_agent.py

echo ""
echo "✅ 测试完成！"