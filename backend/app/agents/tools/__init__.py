# backend/app/agents/tools/__init__.py
"""
学习工具集模块
提供英语学习相关的专用工具
"""

from .learning_tools import (
    search_dictionary,
    get_word_definitions,
    create_vocabulary_exercise,
    get_user_progress,
    get_review_words,
    mark_word_completed,
    search_pronunciation,
    get_grammar_explanation,
    create_conversation_practice
)

__all__ = [
    "search_dictionary",
    "get_word_definitions",
    "create_vocabulary_exercise",
    "get_user_progress",
    "get_review_words",
    "mark_word_completed",
    "search_pronunciation",
    "get_grammar_explanation",
    "create_conversation_practice"
]