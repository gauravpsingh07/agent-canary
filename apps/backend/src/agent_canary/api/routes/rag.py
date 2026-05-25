from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import SessionLocal, get_db
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


def _ingest_document_in_background(payload: RagDocumentCreate) -> None:
    session = SessionLocal()
    try:
        ingest_document(session, payload)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@router.post(
    "/rag/documents",
    response_model=DocumentIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rag_document(
    payload: RagDocumentCreate,
    db: DbSession,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(default=False),
) -> DocumentIngestionResponse:
    ensure_project_exists(db, payload.project_id)
    if async_mode:
        # Create a placeholder document row + queued ingestion job; do the work off-thread.
        document = RagDocument(
            project_id=payload.project_id,
            title=payload.title,
            source_type=payload.source_type,
            source_uri=payload.source_uri,
            content_hash="pending",
            status="pending",
            document_metadata=payload.metadata,
        )
        db.add(document)
        db.flush()
        job = DocumentIngestionJob(
            project_id=payload.project_id,
            document_id=document.id,
            status="queued",
            job_metadata={"mode": "background"},
        )
        db.add(job)
        db.commit()
        db.refresh(document)
        db.refresh(job)
        background_tasks.add_task(_ingest_document_in_background, payload)
        return DocumentIngestionResponse(
            document=RagDocumentRead.model_validate(document),
            ingestion_job=DocumentIngestionJobRead.model_validate(job),
            chunks_created=0,
        )

    outcome = ingest_document(db, payload)
    db.commit()
    db.refresh(outcome.document)
    db.refresh(outcome.ingestion_job)
    return DocumentIngestionResponse(
        document=RagDocumentRead.model_validate(outcome.document),
        ingestion_job=DocumentIngestionJobRead.model_validate(outcome.ingestion_job),
        chunks_created=outcome.chunks_created,
    )


@router.post(
    "/rag/documents/{document_id}/ingest",
    response_model=DocumentIngestionResponse,
)
def reingest_rag_document(
    document_id: str,
    payload: RagDocumentCreate,
    db: DbSession,
) -> DocumentIngestionResponse:
    document = get_document_or_404(db, document_id)
    outcome = ingest_document(db, payload, document=document)
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


@router.get("/rag/retrieval-results", response_model=list[RetrievalResultRead])
def list_retrieval_results(
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
    project_id: str | None = None,
    test_run_id: str | None = None,
) -> list[RetrievalResult]:
    statement = select(RetrievalResult).order_by(RetrievalResult.created_at.desc()).limit(limit)
    if project_id is not None:
        statement = statement.where(RetrievalResult.project_id == project_id)
    if test_run_id is not None:
        statement = statement.where(RetrievalResult.test_run_id == test_run_id)
    return list(db.scalars(statement).all())


@router.get("/rag/retrieval-results/{result_id}", response_model=RetrievalResultRead)
def get_retrieval_result(result_id: str, db: DbSession) -> RetrievalResult:
    return get_retrieval_result_or_404(db, result_id)
