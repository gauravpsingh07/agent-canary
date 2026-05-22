from agent_canary.embeddings.mock import MockEmbeddingProvider
from agent_canary.services.rag import cosine_similarity


def test_mock_embedding_provider_is_deterministic_and_normalized() -> None:
    provider = MockEmbeddingProvider(dimensions=32)

    first = provider.embed_text("refund policy")
    second = provider.embed_text("refund policy")

    assert first == second
    assert len(first) == 32
    assert round(cosine_similarity(first, second), 4) == 1.0


def test_mock_embedding_similarity_tracks_shared_terms() -> None:
    provider = MockEmbeddingProvider(dimensions=64)

    query = provider.embed_text("refund policy")
    related = provider.embed_text("refund policy exception")
    unrelated = provider.embed_text("database outage incident")

    assert cosine_similarity(query, related) > cosine_similarity(query, unrelated)
