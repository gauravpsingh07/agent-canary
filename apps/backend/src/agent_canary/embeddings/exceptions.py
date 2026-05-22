class EmbeddingProviderError(RuntimeError):
    pass


class EmbeddingProviderConfigurationError(EmbeddingProviderError):
    pass


class EmbeddingProviderResponseError(EmbeddingProviderError):
    pass
