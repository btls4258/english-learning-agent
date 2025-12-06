# backend/app/agents/tools/learning_tools.py
"""
英语学习专用工具
使用LangChain的@tool装饰器，支持Agent调用
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import random
from datetime import timedelta

# 这些将在运行时通过依赖注入提供
db_session: Optional[AsyncSession] = None
user_id: Optional[int] = None

def set_learning_context(session: AsyncSession, current_user_id: int):
    """设置学习工具的上下文（数据库会话和用户ID）"""
    global db_session, user_id
    db_session = session
    user_id = current_user_id

@tool
def search_dictionary(word: str) -> str:
    """
    在字典中搜索单词的定义和用法

    Args:
        word: 要搜索的英文单词

    Returns:
        单词的定义、音标、例句等详细信息
    """
    # 模拟字典搜索（实际项目可以集成真实的字典API）
    dictionary_data = {
        "hello": {
            "phonetic": "/həˈloʊ/",
            "definition": "用于问候或引起注意的感叹词",
            "examples": [
                "Hello, how are you?",
                "She said hello to her neighbors."
            ]
        },
        "study": {
            "phonetic": "/ˈstʌdi/",
            "definition": "学习；研究；书房",
            "examples": [
                "I need to study for my exam.",
                "He is in his study."
            ]
        }
    }

    word_lower = word.lower()
    if word_lower in dictionary_data:
        data = dictionary_data[word_lower]
        return f"""
📖 **{word}**
🔊 音标: {data['phonetic']}
📝 定义: {data['definition']}
📚 例句:
{chr(10).join(f"  • {ex}" for ex in data['examples'])}
        """.strip()
    else:
        return f"未找到单词 '{word}' 的定义。请检查拼写或尝试其他单词。"

@tool
def get_word_definitions(word_list: List[str]) -> str:
    """
    批量获取单词定义

    Args:
        word_list: 单词列表

    Returns:
        所有单词的定义信息
    """
    results = []
    for word in word_list:
        definition = search_dictionary.run(word)
        results.append(f"**{word}**: {definition}")

    return "\n\n".join(results)

@tool
def create_vocabulary_exercise(topic: str, difficulty: str = "intermediate") -> str:
    """
    创建词汇练习题

    Args:
        topic: 练习主题（如：animals, food, travel）
        difficulty: 难度级别（beginner, intermediate, advanced）

    Returns:
        生成的练习题内容
    """
    exercises = {
        "animals": [
            {
                "question": "What do you call a baby cat?",
                "options": ["puppy", "kitten", "cub", "foal"],
                "answer": "kitten"
            },
            {
                "question": "Which animal is known as 'man's best friend'?",
                "options": ["cat", "dog", "horse", "rabbit"],
                "answer": "dog"
            }
        ],
        "food": [
            {
                "question": "What fruit is known as 'the king of fruits'?",
                "options": ["apple", "banana", "mango", "orange"],
                "answer": "mango"
            }
        ]
    }

    if topic not in exercises:
        return f"主题 '{topic}' 的练习题正在准备中。请尝试：animals, food"

    exercise = random.choice(exercises[topic])

    return f"""
📝 **词汇练习 - {topic.title()} ({difficulty})**

❓ 问题: {exercise['question']}
🔘 选项:
{chr(10).join(f"  {chr(65+i)}. {opt}" for i, opt in enumerate(exercise['options']))}

💡 提示：仔细思考后选择答案，答案将在下次对话中揭晓。
    """.strip()

@tool
def get_user_progress() -> str:
    """
    获取用户当前的学习进度

    Returns:
        用户的学习进度统计信息
    """
    if not db_session or not user_id:
        return "无法获取用户信息，请确保已正确登录。"

    # 这里需要导入模型，避免循环导入
    from app.models import UserWordProgress, Word

    try:
        # 获取用户的所有学习记录
        stmt = select(UserWordProgress).where(UserWordProgress.user_id == user_id)
        # 由于这是同步工具函数，我们需要使用同步方式执行
        import asyncio
        result = asyncio.run(db_session.execute(stmt))
        progress_records = result.scalars().all()

        if not progress_records:
            return "你还没有开始学习任何单词。开始你的学习之旅吧！"

        # 统计信息
        total_words = len(progress_records)
        mastered_words = sum(1 for p in progress_records if p.is_mastered)
        reviewing_today = sum(1 for p in progress_records
                            if p.next_review_at and p.next_review_at <= datetime.now())

        avg_proficiency = sum(p.proficiency for p in progress_records) / total_words if total_words > 0 else 0

        return f"""
📊 **你的学习进度**

📚 已学习单词: {total_words} 个
✅ 已掌握单词: {mastered_words} 个
🔄 今日待复习: {reviewing_today} 个
📈 平均熟练度: {avg_proficiency:.1f}%

继续加油！每一步都是进步 💪
        """.strip()

    except Exception as e:
        return f"获取学习进度时出现错误：{str(e)}"

@tool
def get_review_words() -> str:
    """
    获取需要复习的单词列表

    Returns:
        今日待复习的单词
    """
    if not db_session or not user_id:
        return "无法获取复习列表，请确保已正确登录。"

    from app.models import UserWordProgress, Word

    try:
        stmt = select(UserWordProgress, Word).join(Word).where(
            UserWordProgress.user_id == user_id,
            UserWordProgress.next_review_at <= datetime.now()
        ).limit(10)  # 限制返回数量

        import asyncio
        result = asyncio.run(db_session.execute(stmt))
        review_items = result.all()

        if not review_items:
            return "太棒了！今天没有需要复习的单词 🎉"

        words_info = []
        for progress, word in review_items:
            words_info.append(f"• **{word.spelling}** - {word.meaning}")

        return f"""
📖 **今日复习清单** ({len(review_items)} 个单词)

{chr(10).join(words_info)}

准备好开始复习了吗？
        """.strip()

    except Exception as e:
        return f"获取复习列表时出现错误：{str(e)}"

@tool
def mark_word_completed(word_id: int, quality: int) -> str:
    """
    标记单词学习完成并更新记忆强度

    Args:
        word_id: 单词ID
        quality: 学习质量评分 (0-5，0=完全不记得，5=完全掌握)

    Returns:
        更新结果和下次复习时间
    """
    if not db_session or not user_id:
        return "无法更新学习记录，请确保已正确登录。"

    from app.models import UserWordProgress

    try:
        # 查找学习记录
        stmt = select(UserWordProgress).where(
            UserWordProgress.user_id == user_id,
            UserWordProgress.word_id == word_id
        )
        import asyncio
        result = asyncio.run(db_session.execute(stmt))
        progress = result.scalar_one_or_none()

        if not progress:
            return f"未找到单词ID {word_id} 的学习记录。"

        # 更新SM-2算法参数
        q = max(0, min(5, quality))  # 确保在0-5范围内
        ef = progress.easiness_factor
        reps = progress.repetitions
        interval = progress.interval

        # SM-2算法逻辑
        if q < 3:
            reps = 0
            interval = 1
        else:
            new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
            ef = max(1.3, new_ef)
            reps += 1

            if reps == 1:
                interval = 1
            elif reps == 2:
                interval = 6
            else:
                interval = int(interval * ef)

        # 更新记录
        progress.easiness_factor = ef
        progress.repetitions = reps
        progress.interval = interval
        progress.last_reviewed_at = datetime.now()
        progress.next_review_at = datetime.now() + timedelta(days=interval)
        progress.proficiency = min(reps * 20, 100)

        if quality >= 4:
            progress.is_mastered = True

        asyncio.run(db_session.commit())

        next_review = progress.next_review_at.strftime("%Y-%m-%d %H:%M")

        return f"""
✅ **学习记录已更新**

📊 记忆强度: {ef:.2f}
🔄 复习间隔: {interval} 天
📈 熟练度: {progress.proficiency}%
⏰ 下次复习: {next_review}

{ "🎉 恭喜！你已经掌握了这个单词！" if progress.is_mastered else "" }
        """.strip()

    except Exception as e:
        return f"更新学习记录时出现错误：{str(e)}"

@tool
def search_pronunciation(word: str) -> str:
    """
    搜索单词的发音信息

    Args:
        word: 要查询发音的单词

    Returns:
        音标、发音要点和相似单词
    """
    pronunciation_data = {
        "hello": {
            "phonetic": "/həˈloʊ/",
            "syllables": "he-llo (2音节)",
            "stress": "重音在第二个音节",
            "similar_sounds": ["hollow", "yellow"]
        },
        "world": {
            "phonetic": "/wɜːrld/",
            "syllables": "world (1音节)",
            "stress": "单音节词",
            "tip": "注意 'rl' 连读，舌头不要碰到上颚",
            "similar_sounds": ["word", "work"]
        }
    }

    word_lower = word.lower()
    if word_lower in pronunciation_data:
        data = pronunciation_data[word_lower]

        result = f"""
🔊 **{word} 发音指南**

📝 音标: {data['phonetic']}
🎵 音节: {data['syllables']}
💪 重音: {data['stress']}
        """

        if 'tip' in data:
            result += f"\n💡 发音要点: {data['tip']}"

        if 'similar_sounds' in data:
            result += f"\n🔄 相似发音: {', '.join(data['similar_sounds'])}"

        return result.strip()
    else:
        return f"暂时没有 '{word}' 的发音数据。建议查阅在线词典获取更准确的发音信息。"

@tool
def get_grammar_explanation(grammar_point: str) -> str:
    """
    获取语法点的详细解释

    Args:
        grammar_point: 语法点名称（如：present tense, articles, prepositions）

    Returns:
        语法规则、用法和例句
    """
    grammar_data = {
        "present tense": {
            "rule": "现在时用于描述当前的动作或状态",
            "forms": [
                "I/You/We/They + 动词原形",
                "He/She/It + 动词-s/es形式"
            ],
            "examples": [
                "I study English every day.",
                "She works in a hospital.",
                "They play football on weekends."
            ],
            "common_mistakes": [
                "忘记第三人称单数加-s",
                "在一般现在时使用be动词不当"
            ]
        },
        "articles": {
            "rule": "冠词用于说明名词是特指还是泛指",
            "types": [
                "a/an - 不定冠词，用于泛指",
                "the - 定冠词，用于特指"
            ],
            "examples": [
                "I saw a dog in the park. (第一次提到)",
                "The dog was very friendly. (再次提到)"
            ],
            "tips": "a用在辅音开头的词前，an用在元音开头的词前"
        }
    }

    grammar_lower = grammar_point.lower()
    if grammar_lower in grammar_data:
        data = grammar_data[grammar_lower]

        result = f"""
📖 **语法详解: {grammar_point.title()}**

📋 规则: {data['rule']}

🔧 用法:
{chr(10).join(f"  • {form}" for form in data['forms'])}

📚 例句:
{chr(10).join(f"  • {ex}" for ex in data['examples'])}
        """

        if 'common_mistakes' in data:
            result += f"\n⚠️ 常见错误:"
            result += chr(10).join(f"  • {mistake}" for mistake in data['common_mistakes'])

        if 'tips' in data:
            result += f"\n💡 小贴士: {data['tips']}"

        return result.strip()
    else:
        return f"暂时没有 '{grammar_point}' 的语法解释。请尝试：present tense, articles, prepositions"

@tool
def create_conversation_practice(topic: str, level: str = "intermediate") -> str:
    """
    创建对话练习场景

    Args:
        topic: 对话主题（如：restaurant, shopping, job interview）
        level: 难度级别（beginner, intermediate, advanced）

    Returns:
        对话场景和相关表达
    """
    conversations = {
        "restaurant": {
            "intermediate": {
                "situation": "在餐厅点餐和结账",
                "dialogue": [
                    "Waiter: Good evening, welcome to our restaurant.",
                    "Customer: Hi, I'd like a table for two please.",
                    "Waiter: Certainly. Here's your menu.",
                    "Customer: Thank you. I'll have the steak and my friend will have the fish.",
                    "Waiter: Excellent choice. Anything to drink?",
                    "Customer: Yes, we'll have two glasses of water.",
                    "Waiter: Perfect. Your order will be ready soon."
                ],
                "useful_phrases": [
                    "I'd like to order...",
                    "Could we have the bill, please?",
                    "What do you recommend?",
                    "Is this dish spicy?"
                ]
            }
        },
        "shopping": {
            "intermediate": {
                "situation": "在商店购物和询问价格",
                "dialogue": [
                    "Shop assistant: Hello, can I help you find anything?",
                    "Customer: Yes, I'm looking for a gift for my friend.",
                    "Shop assistant: What kind of gift are you thinking of?",
                    "Customer: Maybe a book or something decorative.",
                    "Shop assistant: We have some lovely options over here.",
                    "Customer: How much does this cost?",
                    "Shop assistant: It's $25, but there's a 10% discount today."
                ],
                "useful_phrases": [
                    "I'm looking for...",
                    "How much does this cost?",
                    "Do you have this in another color?",
                    "Can I try this on?"
                ]
            }
        }
    }

    if topic not in conversations or level not in conversations[topic]:
        available_topics = ", ".join(conversations.keys())
        return f"主题 '{topic}' 或难度 '{level}' 的对话练习暂未准备好。可用主题：{available_topics}"

    conv = conversations[topic][level]

    return f"""
💬 **对话练习 - {topic.title()} ({level})**

🎭 场景: {conv['situation']}

🗣️ 示例对话:
{chr(10).join(f"  {line}" for line in conv['dialogue'])}

💡 实用表达:
{chr(10).join(f"  • {phrase}" for phrase in conv['useful_phrases'])}

🎯 练习建议：和朋友一起角色扮演，或者自己练习不同角色的对话。
    """.strip()