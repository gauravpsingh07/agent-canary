from agent_canary.core.config import Settings, get_settings
from agent_canary.llm.base import LLMProvider
from agent_canary.llm.exceptions import LLMProviderConfigurationError
from agent_canary.llm.gemini import GeminiProvider
from agent_canary.llm.groq import GroqProvider
from agent_canary.llm.mock import MockLLMProvider
from agent_canary.llm.openai import OpenAIProvider


def build_llm_provider(settings: Settings | None = None) -> LLMProvider:
    resolved_settings = settings or get_settings()
    provider_name = resolved_settings.llm_provider.strip().lower()

    if provider_name == "mock":
        return MockLLMProvider(model_name=resolved_settings.mock_llm_model)

    if provider_name == "gemini":
        return GeminiProvider(
            api_key=resolved_settings.gemini_api_key,
            model_name=resolved_settings.gemini_model,
            timeout_seconds=resolved_settings.llm_timeout_seconds,
        )

    if provider_name == "groq":
        return GroqProvider(
            api_key=resolved_settings.groq_api_key,
            model_name=resolved_settings.groq_model,
            timeout_seconds=resolved_settings.llm_timeout_seconds,
        )

    if provider_name == "openai":
        return OpenAIProvider(
            api_key=resolved_settings.openai_api_key,
            model_name=resolved_settings.openai_model,
            timeout_seconds=resolved_settings.llm_timeout_seconds,
        )

    raise LLMProviderConfigurationError(
        f"Unsupported LLM_PROVIDER '{resolved_settings.llm_provider}'"
    )

