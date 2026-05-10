"""LangChain LLM 服务模块"""

import os
from langchain_openai import ChatOpenAI
from ..config import get_settings

_llm_instance = None


def get_llm() -> ChatOpenAI:
    """
    获取 LangChain ChatOpenAI 实例，兼容 OpenAI / DeepSeek / 其他 OpenAI-compatible 服务。
    """
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()

        api_key = (
            os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or settings.openai_api_key
        )

        base_url = (
            os.getenv("LLM_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or settings.openai_base_url
        )

        model = (
            os.getenv("LLM_MODEL_ID")
            or os.getenv("OPENAI_MODEL")
            or settings.openai_model
        )

        if not api_key:
            raise ValueError("未配置 LLM_API_KEY 或 OPENAI_API_KEY")

        _llm_instance = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.3,
        )

        print("✅ LangChain LLM 初始化成功")
        print(f"   Base URL: {base_url}")
        print(f"   Model: {model}")

    return _llm_instance


def reset_llm():
    """重置 LLM 实例"""
    global _llm_instance
    _llm_instance = None