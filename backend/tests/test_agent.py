#!/usr/bin/env python3
"""
简化的Agent测试脚本
验证新的英语学习Agent功能
"""

import asyncio
import sys
import os
from typing import Dict, Any, List

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from app.agents.english_learning_agent import EnglishLearningAgent, agent_manager
from app.agents.llm_providers import get_llm
from app.agents.tools.learning_tools import (
    search_dictionary,
    create_vocabulary_exercise,
    get_grammar_explanation,
    get_user_progress
)


class SimpleAgentTester:
    """简化的Agent测试器"""

    def __init__(self):
        self.test_results = []

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if message:
            print(f"    {message}")

        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    async def test_agent_creation(self):
        """测试Agent创建"""
        print("🤖 测试Agent创建...")

        try:
            # 测试Agent初始化
            agent = EnglishLearningAgent(provider="deepseek")
            self.log_result("Agent初始化", True)

            # 测试工具加载
            agent_info = agent.get_agent_info()
            expected_tools = 9
            actual_tools = agent_info["tools_count"]
            self.log_result(
                "工具数量检查",
                actual_tools == expected_tools,
                f"期望{expected_tools}个工具，实际{actual_tools}个"
            )

            # 测试系统提示词
            has_prompt = "Emma" in agent.system_prompt
            self.log_result("系统提示词", has_prompt)

        except Exception as e:
            self.log_result("Agent创建", False, str(e))

    def test_tools_functionality(self):
        """测试工具功能"""
        print("\n🔧 测试工具功能...")

        try:
            # 测试字典搜索
            result = search_dictionary.invoke({"word": "hello"})
            has_content = "hello" in result.lower() and len(result) > 10
            self.log_result("字典搜索工具", has_content)

            # 测试词汇练习
            exercise = create_vocabulary_exercise.invoke({"topic": "animals", "difficulty": "beginner"})
            has_exercise = "animals" in exercise.lower() and "练习" in exercise
            self.log_result("词汇练习工具", has_exercise)

            # 测试语法解释
            grammar = get_grammar_explanation.invoke({"grammar_point": "present tense"})
            has_grammar = "present tense" in grammar.lower() and "规则" in grammar
            self.log_result("语法解释工具", has_grammar)

            # 测试进度查询（无数据库上下文）
            progress = get_user_progress.invoke({})
            has_progress_msg = "无法获取用户信息" in progress or "还没有开始学习" in progress
            self.log_result("学习进度工具", has_progress_msg)

        except Exception as e:
            self.log_result("工具功能", False, str(e))

    def test_agent_manager(self):
        """测试Agent管理器"""
        print("\n👥 测试Agent管理器...")

        try:
            # 创建不同用户的Agent
            agent1 = agent_manager.get_agent(user_id=1, provider="deepseek")
            agent2 = agent_manager.get_agent(user_id=2, provider="glm4")

            # 测试Agent复用
            agent1_again = agent_manager.get_agent(user_id=1)
            is_same = agent1 is agent1_again
            self.log_result("Agent复用", is_same, "相同用户ID应返回同一Agent实例")

            # 测试不同用户Agent
            is_different = agent1 is not agent2
            self.log_result("多用户支持", is_different, "不同用户应有独立Agent实例")

            # 测试管理器信息
            all_agents = agent_manager.get_all_agents_info()
            has_users = 1 in all_agents and 2 in all_agents
            self.log_result("Agent信息管理", has_users, f"管理器应包含2个用户Agent")

            # 清理测试数据
            agent_manager.clear_all_agents()
            is_empty = len(agent_manager.get_all_agents_info()) == 0
            self.log_result("Agent清理", is_empty)

        except Exception as e:
            self.log_result("Agent管理器", False, str(e))

    def test_user_context(self):
        """测试用户上下文"""
        print("\n👤 测试用户上下文...")

        try:
            # 测试上下文创建
            context = {"level": "intermediate", "goals": ["conversation", "vocabulary"]}
            agent = EnglishLearningAgent(provider="deepseek", user_context=context)

            # 检查上下文设置
            current_context = agent.get_user_context()
            has_level = current_context.get("level") == "intermediate"
            has_goals = current_context.get("goals") == ["conversation", "vocabulary"]
            self.log_result("上下文创建", has_level and has_goals)

            # 测试上下文更新
            agent.update_user_context(level="advanced", new_goal="business")
            updated_context = agent.get_user_context()
            level_updated = updated_context.get("level") == "advanced"
            has_new_goal = updated_context.get("new_goal") == "business"
            self.log_result("上下文更新", level_updated and has_new_goal)

            # 测试系统提示词包含上下文
            prompt = agent.system_prompt
            has_context_in_prompt = "intermediate" in prompt or "advanced" in prompt
            self.log_result("提示词个性化", has_context_in_prompt, "系统提示词应包含用户水平信息")

        except Exception as e:
            self.log_result("用户上下文", False, str(e))

    async def test_agent_conversation(self):
        """测试Agent对话（模拟）"""
        print("\n💬 测试Agent对话能力...")

        try:
            # 创建Agent
            agent = EnglishLearningAgent(provider="deepseek")

            # 测试对话历史管理
            agent.chat("Hello")
            history = agent.get_history()
            has_history = len(history) >= 2  # 用户消息 + AI消息
            self.log_result("对话历史管理", has_history, f"对话历史应有2条消息，实际{len(history)}条")

            # 测试清空历史
            agent.clear_history()
            history_cleared = len(agent.get_history()) == 0
            self.log_result("清空对话历史", history_cleared)

            # 测试上下文清理
            agent_info = agent.get_agent_info()
            has_info = "provider" in agent_info and "tools_count" in agent_info
            self.log_result("Agent信息获取", has_info)

        except Exception as e:
            self.log_result("Agent对话", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 英语学习Agent - 简化测试套件")
        print("=" * 50)

        # 运行异步测试
        await self.test_agent_creation()
        await self.test_agent_conversation()

        # 运行同步测试
        self.test_tools_functionality()
        self.test_agent_manager()
        self.test_user_context()

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📋 测试报告")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(r["success"] for r in self.test_results)
        failed_tests = total_tests - passed_tests

        # 显示详细结果
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
            if result["message"] and not result["success"]:
                print(f"    💡 {result['message']}")

        # 显示统计信息
        print(f"\n📊 测试统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {passed_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {(passed_tests/total_tests*100):.1f}%")

        # 总结
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！英语学习Agent功能正常！")
            print("\n🚀 可以启动服务器:")
            print("  cd backend && python -m uvicorn app.main:app --reload")
            print("\n📱 启动前端:")
            print("  cd frontend && flutter run")
        else:
            print(f"\n⚠️  有{failed_tests}个测试失败，请检查相关功能")
            print("\n💡 建议修复后再启动服务器")

        print("=" * 50)


def main():
    """主函数"""
    tester = SimpleAgentTester()
    asyncio.run(tester.run_all_tests())


if __name__ == "__main__":
    main()