from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.core.config import Settings, get_settings
from agent_canary.embeddings import EmbeddingProvider, build_embedding_provider
from agent_canary.models import (
    DocumentIngestionJob,
    RagChunk,
    RagDocument,
    RetrievalResult,
)
from agent_canary.models.base import utc_now
from agent_canary.schemas import RagDocumentCreate, RetrievalRequest
from agent_canary.services.audit import write_audit_log
from agent_canary.services.chunking import chunk_text, normalize_text


@dataclass(frozen=True)
class IngestionOutcome:
    document: RagDocument
    ingestion_job: DocumentIngestionJob
    chunks_created: int


def ingest_document(
    db: Session,
    payload: RagDocumentCreate,
    *,
    provider: EmbeddingProvider | None = None,
    settings: Settings | None = None,
) -> IngestionOutcome:
    resolved_settings = settings or get_settings()
    resolved_provider = provider or build_embedding_provider(resolved_settings)
    normalized_content = normalize_text(payload.content)
    document = RagDocument(
        project_id=payload.project_id,
        title=payload.title,
        source_type=payload.source_type,
        source_uri=payload.source_uri,
        content_hash=sha256_text(normalized_content),
        status="indexing",
        document_metadata=payload.metadata,
    )
    db.add(document)
    db.flush()

    job = DocumentIngestionJob(
        project_id=payload.project_id,
        document_id=document.id,
        status="running",
        started_at=utc_now(),
        job_metadata={
            "embedding_provider": resolved_provider.provider_name,
            "embedding_model": resolved_provider.model_name,
        },
    )
    db.add(job)
    db.flush()
    write_audit_log(
        db,
        project_id=payload.project_id,
        entity_type="rag_document",
        entity_id=document.id,
        event_type="DOCUMENT_INGESTION_STARTED",
        metadata={"job_id": job.id, "title": document.title},
    )

    try:
        chunks = chunk_text(
            normalized_content,
            max_chars=resolved_settings.rag_chunk_max_chars,
            overlap_chars=resolved_settings.rag_chunk_overlap_chars,
        )
        embeddings = resolved_provider.embed_batch([chunk.content for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            db.add(
                RagChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    content_hash=sha256_text(chunk.content),
                    token_count=chunk.token_count,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                    embedding=embedding,
                    embedding_vector=to_pgvector_literal(embedding),
                    embedding_provider=resolved_provider.provider_name,
                    embedding_model=resolved_provider.model_name,
                    embedding_dimension=len(embedding),
                    chunk_metadata={},
                )
            )

        document.status = "indexed"
        job.status = "completed"
        job.chunks_created = len(chunks)
        job.completed_at = utc_now()
        write_audit_log(
            db,
            project_id=payload.project_id,
            entity_type="rag_document",
            entity_id=document.id,
            event_type="DOCUMENT_INGESTION_COMPLETED",
            metadata={"job_id": job.id, "chunks_created": len(chunks)},
        )
    except Exception as exc:
        document.status = "failed"
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = utc_now()
        write_audit_log(
            db,
            project_id=payload.project_id,
            entity_type="rag_document",
            entity_id=document.id,
            event_type="DOCUMENT_INGESTION_FAILED",
            metadata={"job_id": job.id, "error": str(exc)},
        )
        raise

    db.flush()
    return IngestionOutcome(document=document, ingestion_job=job, chunks_created=len(chunks))


def retrieve_chunks(
    db: Session,
    payload: RetrievalRequest,
    *,
    provider: EmbeddingProvider | None = None,
    settings: Settings | None = None,
) -> RetrievalResult:
    resolved_settings = settings or get_settings()
    resolved_provider = provider or build_embedding_provider(resolved_settings)
    max_results = payload.max_results or resolved_settings.retrieval_default_max_results
    min_score = (
        payload.min_score
        if payload.min_score is not None
        else resolved_settings.retrieval_default_min_score
    )
    query = normalize_text(payload.query)
    query_embedding = resolved_provider.embed_text(query)

    statement = (
        select(RagChunk)
        .join(RagDocument)
        .where(RagDocument.status == "indexed")
        .order_by(RagDocument.created_at.desc(), RagChunk.chunk_index.asc())
    )
    if payload.project_id is not None:
        statement = statement.where(RagDocument.project_id == payload.project_id)

    scored_results = []
    for chunk in db.scalars(statement).all():
        score = cosine_similarity(query_embedding, chunk.embedding)
        if score < min_score:
            continue
        scored_results.append((score, chunk))

    ranked_results = sorted(scored_results, key=lambda item: item[0], reverse=True)[:max_results]
    result_payload = [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_title": chunk.document.title,
            "source_uri": chunk.document.source_uri,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "score": round(score, 4),
        }
        for score, chunk in ranked_results
    ]
    retrieval_result = RetrievalResult(
        project_id=payload.project_id,
        query=query,
        min_score=min_score,
        max_results=max_results,
        result_count=len(result_payload),
        provider_name=resolved_provider.provider_name,
        model_name=resolved_provider.model_name,
        results=result_payload,
        retrieval_metadata={"embedding_dimension": len(query_embedding)},
    )
    db.add(retrieval_result)
    db.flush()
    write_audit_log(
        db,
        project_id=payload.project_id,
        entity_type="retrieval_result",
        entity_id=retrieval_result.id,
        event_type="RAG_RETRIEVAL_COMPLETED",
        metadata={
            "query": query,
            "result_count": len(result_payload),
            "min_score": min_score,
            "max_results": max_results,
        },
    )
    return retrieval_result


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(
        left_value * right_value for left_value, right_value in zip(left, right, strict=True)
    )
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def to_pgvector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"
