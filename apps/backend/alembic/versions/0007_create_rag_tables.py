"""Create RAG document, chunk, retrieval, and ingestion tables.

Revision ID: 0007_create_rag_tables
Revises: 0006_create_approval_requests
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0007_create_rag_tables"
down_revision = "0006_create_approval_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "rag_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_uri", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_rag_documents_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rag_documents")),
    )
    op.create_index(op.f("ix_rag_documents_project_id"), "rag_documents", ["project_id"])
    op.create_index(op.f("ix_rag_documents_content_hash"), "rag_documents", ["content_hash"])
    op.create_index(op.f("ix_rag_documents_status"), "rag_documents", ["status"])

    op.create_table(
        "document_ingestion_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("chunks_created", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["rag_documents.id"],
            name=op.f("fk_document_ingestion_jobs_document_id_rag_documents"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_document_ingestion_jobs_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_ingestion_jobs")),
    )
    op.create_index(
        op.f("ix_document_ingestion_jobs_document_id"),
        "document_ingestion_jobs",
        ["document_id"],
    )
    op.create_index(
        op.f("ix_document_ingestion_jobs_project_id"),
        "document_ingestion_jobs",
        ["project_id"],
    )
    op.create_index(
        op.f("ix_document_ingestion_jobs_status"),
        "document_ingestion_jobs",
        ["status"],
    )

    op.create_table(
        "rag_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("embedding_vector", sa.Text(), nullable=True),
        sa.Column("embedding_provider", sa.String(length=80), nullable=False),
        sa.Column("embedding_model", sa.String(length=160), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["rag_documents.id"],
            name=op.f("fk_rag_chunks_document_id_rag_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rag_chunks")),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_rag_chunks_document_index"),
    )
    op.execute(
        "ALTER TABLE rag_chunks "
        "ALTER COLUMN embedding_vector TYPE vector(768) "
        "USING embedding_vector::vector"
    )
    op.create_index(op.f("ix_rag_chunks_document_id"), "rag_chunks", ["document_id"])
    op.create_index(op.f("ix_rag_chunks_content_hash"), "rag_chunks", ["content_hash"])
    op.execute(
        "CREATE INDEX ix_rag_chunks_embedding_vector "
        "ON rag_chunks USING ivfflat (embedding_vector vector_cosine_ops)"
    )

    op.create_table(
        "retrieval_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("min_score", sa.Float(), nullable=False),
        sa.Column("max_results", sa.Integer(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_retrieval_results_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_retrieval_results")),
    )
    op.create_index(
        op.f("ix_retrieval_results_project_id"),
        "retrieval_results",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_retrieval_results_project_id"), table_name="retrieval_results")
    op.drop_table("retrieval_results")
    op.execute("DROP INDEX IF EXISTS ix_rag_chunks_embedding_vector")
    op.drop_index(op.f("ix_rag_chunks_content_hash"), table_name="rag_chunks")
    op.drop_index(op.f("ix_rag_chunks_document_id"), table_name="rag_chunks")
    op.drop_table("rag_chunks")
    op.drop_index(op.f("ix_document_ingestion_jobs_status"), table_name="document_ingestion_jobs")
    op.drop_index(
        op.f("ix_document_ingestion_jobs_project_id"),
        table_name="document_ingestion_jobs",
    )
    op.drop_index(
        op.f("ix_document_ingestion_jobs_document_id"),
        table_name="document_ingestion_jobs",
    )
    op.drop_table("document_ingestion_jobs")
    op.drop_index(op.f("ix_rag_documents_status"), table_name="rag_documents")
    op.drop_index(op.f("ix_rag_documents_content_hash"), table_name="rag_documents")
    op.drop_index(op.f("ix_rag_documents_project_id"), table_name="rag_documents")
    op.drop_table("rag_documents")
