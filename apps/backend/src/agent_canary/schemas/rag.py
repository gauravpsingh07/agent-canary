from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RagDocumentCreate(BaseModel):
    project_id: str | None = None
    title: str = Field(min_length=1, max_length=240)
    content: str = Field(min_length=1)
    source_type: str = Field(default="manual", min_length=1, max_length=80)
    source_uri: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    title: str
    source_type: str
    source_uri: str | None
    content_hash: str
    status: str
    document_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class RagChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    chunk_index: int
    content: str
    content_hash: str
    token_count: int
    char_start: int
    char_end: int
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
    chunk_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class DocumentIngestionJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    document_id: str | None
    status: str
    chunks_created: int
    error_message: str | None
    job_metadata: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DocumentIngestionResponse(BaseModel):
    document: RagDocumentRead
    ingestion_job: DocumentIngestionJobRead
    chunks_created: int


class RetrievalRequest(BaseModel):
    project_id: str | None = None
    query: str = Field(min_length=1)
    max_results: int | None = Field(default=None, ge=1, le=20)
    min_score: float | None = Field(default=None, ge=0, le=1)


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    source_uri: str | None
    chunk_index: int
    content: str
    score: float


class RetrievalResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    test_run_id: str | None
    query: str
    min_score: float
    max_results: int
    result_count: int
    provider_name: str
    model_name: str
    results: list[dict[str, Any]]
    retrieval_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class RagDemoSeedResponse(BaseModel):
    project_id: str
    documents_created: int
    suites_created: int
    test_cases_created: int
    total_rag_documents: int
    total_rag_test_cases: int
