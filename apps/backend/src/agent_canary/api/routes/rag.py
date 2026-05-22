from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import (
    DocumentIngestionJob,
    Project,
    RagChunk,
    RagDocument,
    RetrievalResult,
)
from agent_canary.schemas import (
    DocumentIngestionJobRead,
    DocumentIngestionResponse,
    RagChunkRead,
    RagDemoSeedResponse,
    RagDocumentCreate,
    RagDocumentRead,
    RetrievalRequest,
    RetrievalResultRead,
)
from agent_canary.services.rag import ingest_document, retrieve_chunks
from agent_canary.services.rag_seed import seed_rag_demo_data

router = APIRouter(tags=["rag"])
DbSession = Annotated[Session, Depends(get_db)]


def ensure_project_exists(db: Session, project_id: str | None) -> None:
    if project_id is None:
        return
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


def get_document_or_404(db: Session, document_id: str) -> RagDocument:
    document = db.get(RagDocument, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RAG document not found")
    return document


def get_retrieval_result_or_404(db: Session, result_id: str) -> RetrievalResult:
    result = db.get(RetrievalResult, result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retrieval result not found",
        )
    return result


@router.post(
    "/rag/documents",
    response_model=DocumentIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rag_document(payload: RagDocumentCreate, db: DbSession) -> DocumentIngestionResponse:
    ensure_project_exists(db, payload.project_id)
    outcome = ingest_document(db, payload)
    db.commit()
    db.refresh(outcome.document)
    db.refresh(outcome.ingestion_job)
    return DocumentIngestionResponse(
        document=RagDocumentRead.model_validate(outcome.document),
        ingestion_job=DocumentIngestionJobRead.model_validate(outcome.ingestion_job),
        chunks_created=outcome.chunks_created,
    )


@router.post("/projects/{project_id}/seed-rag-demo-data", response_model=RagDemoSeedResponse)
def seed_project_rag_demo_data(project_id: str, db: DbSession) -> RagDemoSeedResponse:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    (
        documents_created,
        suites_created,
        test_cases_created,
        total_documents,
        total_test_cases,
    ) = seed_rag_demo_data(db, project)
    db.commit()
    return RagDemoSeedResponse(
        project_id=project.id,
        documents_created=documents_created,
        suites_created=suites_created,
        test_cases_created=test_cases_created,
        total_rag_documents=total_documents,
        total_rag_test_cases=total_test_cases,
    )


@router.get("/rag/documents", response_model=list[RagDocumentRead])
def list_rag_documents(db: DbSession) -> list[RagDocument]:
    statement = select(RagDocument).order_by(RagDocument.created_at.desc())
    return list(db.scalars(statement).all())


@router.get("/rag/documents/{document_id}", response_model=RagDocumentRead)
def get_rag_document(document_id: str, db: DbSession) -> RagDocument:
    return get_document_or_404(db, document_id)


@router.get("/rag/documents/{document_id}/chunks", response_model=list[RagChunkRead])
def list_rag_document_chunks(document_id: str, db: DbSession) -> list[RagChunk]:
    get_document_or_404(db, document_id)
    statement = (
        select(RagChunk)
        .where(RagChunk.document_id == document_id)
        .order_by(RagChunk.chunk_index.asc())
    )
    return list(db.scalars(statement).all())


@router.get("/rag/ingestion-jobs", response_model=list[DocumentIngestionJobRead])
def list_document_ingestion_jobs(db: DbSession) -> list[DocumentIngestionJob]:
    statement = select(DocumentIngestionJob).order_by(DocumentIngestionJob.created_at.desc())
    return list(db.scalars(statement).all())


@router.post("/rag/retrieve", response_model=RetrievalResultRead)
def retrieve_rag_chunks(payload: RetrievalRequest, db: DbSession) -> RetrievalResult:
    ensure_project_exists(db, payload.project_id)
    result = retrieve_chunks(db, payload)
    db.commit()
    db.refresh(result)
    return result


@router.get("/rag/retrieval-results/{result_id}", response_model=RetrievalResultRead)
def get_retrieval_result(result_id: str, db: DbSession) -> RetrievalResult:
    return get_retrieval_result_or_404(db, result_id)
