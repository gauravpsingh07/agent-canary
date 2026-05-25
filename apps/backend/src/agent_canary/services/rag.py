from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, text
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
    document: RagDocument | None = None,
) -> IngestionOutcome:
    """Ingest or re-ingest a document.

    If ``document`` is provided, replace its chunks with the new content instead of
    creating a new document row.
    """

    resolved_settings = settings or get_settings()
    resolved_provider = provider or build_embedding_provider(resolved_settings)
    normalized_content = normalize_text(payload.content)

    if document is None:
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
    else:
        # Replace prior chunks; mark document re-indexing.
        for existing_chunk in list(document.chunks):
            db.delete(existing_chunk)
        document.title = payload.title
        document.source_type = payload.source_type
        document.source_uri = payload.source_uri
        document.content_hash = sha256_text(normalized_content)
        document.status = "indexing"
        if payload.metadata:
            document.document_metadata = payload.metadata
        db.flush()

    project_id = payload.project_id or document.project_id

    job = DocumentIngestionJob(
        project_id=project_id,
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
        project_id=project_id,
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
        write_audit_log(
            db,
            project_id=project_id,
            entity_type="rag_document",
            entity_id=document.id,
            event_type="EMBEDDINGS_GENERATED",
            metadata={
                "chunk_count": len(chunks),
                "embedding_provider": resolved_provider.provider_name,
                "embedding_model": resolved_provider.model_name,
                "embedding_dimension": (
                    len(embeddings[0]) if embeddings else resolved_provider.dimensions
                ),
            },
        )
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
            project_id=project_id,
            entity_type="rag_document",
            entity_id=document.id,
            event_type="DOCUMENT_INGESTION_COMPLETED",
            metadata={"job_id": job.id, "chunks_created": len(chunks)},
        )
        write_audit_log(
            db,
            project_id=project_id,
            entity_type="rag_document",
            entity_id=document.id,
            event_type="DOCUMENT_INGESTED",
            metadata={"chunks_created": len(chunks), "title": document.title},
        )
    except Exception as exc:
        document.status = "failed"
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = utc_now()
        write_audit_log(
            db,
            project_id=project_id,
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
    test_run_id: str | None = None,
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

    dialect_name = db.bind.dialect.name if db.bind is not None else ""
    use_pgvector = dialect_name == "postgresql"

    scored_results: list[tuple[float, RagChunk]] = []

    if use_pgvector:
        # Use pgvector cosine distance via raw SQL so we get an indexed ANN-friendly query.
        query_literal = to_pgvector_literal(query_embedding)
        rows = db.execute(
            text(
                """
                SELECT rc.id AS chunk_id,
                       (1 - (rc.embedding_vector <=> CAST(:query AS vector))) AS similarity
                  FROM rag_chunks rc
                  JOIN rag_documents rd ON rd.id = rc.document_id
                 WHERE rd.status = 'indexed'
                   AND (:project_id IS NULL OR rd.project_id = :project_id)
                 ORDER BY rc.embedding_vector <=> CAST(:query AS vector)
                 LIMIT :limit_n
                """
            ),
            {
                "query": query_literal,
                "project_id": payload.project_id,
                "limit_n": max_results * 4,
            },
        ).all()
        chunk_id_to_score = {row.chunk_id: float(row.similarity) for row in rows}
        if chunk_id_to_score:
            chunks = db.scalars(
                select(RagChunk).where(RagChunk.id.in_(chunk_id_to_score.keys()))
            ).all()
            for chunk in chunks:
                score = chunk_id_to_score.get(chunk.id, 0.0)
                if score >= min_score:
                    scored_results.append((score, chunk))
    else:
        statement = (
            select(RagChunk)
            .join(RagDocument)
            .where(RagDocument.status == "indexed")
            .order_by(RagDocument.created_at.desc(), RagChunk.chunk_index.asc())
        )
        if payload.project_id is not None:
            statement = statement.where(RagDocument.project_id == payload.project_id)

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
            "rank": index + 1,
            "used_in_answer": False,
        }
        for index, (score, chunk) in enumerate(ranked_results)
    ]
    retrieval_result = RetrievalResult(
        project_id=payload.project_id,
        test_run_id=test_run_id,
        query=query,
        min_score=min_score,
        max_results=max_results,
        result_count=len(result_payload),
        provider_name=resolved_provider.provider_name,
        model_name=resolved_provider.model_name,
        results=result_payload,
        retrieval_metadata={
            "embedding_dimension": len(query_embedding),
            "dialect": dialect_name or "unknown",
            "pgvector": use_pgvector,
        },
    )
    db.add(retrieval_result)
    db.flush()
    write_audit_log(
        db,
        project_id=payload.project_id,
        entity_type="retrieval_result",
        entity_id=retrieval_result.id,
        event_type="RETRIEVAL_COMPLETED",
        metadata={
            "query": query,
            "result_count": len(result_payload),
            "min_score": min_score,
            "max_results": max_results,
            "test_run_id": test_run_id,
        },
    )
    # Keep the legacy event name in addition so older audit-log consumers stay green.
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


def mark_used_in_answer(
    db: Session,
    retrieval_result_id: str,
    cited_chunk_ids: set[str],
) -> None:
    retrieval = db.get(RetrievalResult, retrieval_result_id)
    if retrieval is None:
        return
    updated: list[dict[str, Any]] = []
    for entry in retrieval.results:
        if isinstance(entry, dict):
            new_entry = dict(entry)
            chunk_id = new_entry.get("chunk_id")
            new_entry["used_in_answer"] = bool(
                chunk_id is not None and str(chunk_id) in cited_chunk_ids
            )
            updated.append(new_entry)
    retrieval.results = updated
    db.flush()


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


def sha256_text(text_value: str) -> str:
    return hashlib.sha256(text_value.encode("utf-8")).hexdigest()


def to_pgvector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"
