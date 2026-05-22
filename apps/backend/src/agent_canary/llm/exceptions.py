class LLMProviderError(RuntimeError):
    """Base error for LLM provider failures."""


class LLMProviderConfigurationError(LLMProviderError):
    """Raised when a provider is selected without required configuration."""


class LLMProviderResponseError(LLMProviderError):
    """Raised when a provider response cannot be parsed into the expected shape."""

