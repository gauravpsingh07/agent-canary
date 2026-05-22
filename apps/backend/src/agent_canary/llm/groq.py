import httpx

from agent_canary.llm.openai_compatible import OpenAICompatibleChatProvider


class GroqProvider(OpenAICompatibleChatProvider):
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            provider_name="groq",
            api_key=api_key,
            model_name=model_name,
            base_url="https://api.groq.com/openai/v1",
            timeout_seconds=timeout_seconds,
            client=client,
        )

