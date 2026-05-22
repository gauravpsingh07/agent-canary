from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import Project, TestSuite
from agent_canary.schemas import TestSuiteCreate, TestSuiteRead, TestSuiteUpdate
from agent_canary.services.audit import write_audit_log

router = APIRouter(tags=["test suites"])
DbSession = Annotated[Session, Depends(get_db)]


def get_project_or_404(db: Session, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def get_test_suite_or_404(db: Session, suite_id: str) -> TestSuite:
    test_suite = db.get(TestSuite, suite_id)
    if test_suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test suite not found")
    return test_suite


@router.get("/projects/{project_id}/test-suites", response_model=list[TestSuiteRead])
def list_test_suites(project_id: str, db: DbSession) -> list[TestSuite]:
    get_project_or_404(db, project_id)
    statement = (
        select(TestSuite)
        .where(TestSuite.project_id == project_id)
        .order_by(TestSuite.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.post(
    "/projects/{project_id}/test-suites",
    response_model=TestSuiteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_test_suite(
    project_id: str,
    payload: TestSuiteCreate,
    db: DbSession,
) -> TestSuite:
    project = get_project_or_404(db, project_id)
    test_suite = TestSuite(project_id=project.id, **payload.model_dump())
    db.add(test_suite)
    db.flush()
    write_audit_log(
        db,
        project_id=project.id,
        entity_type="test_suite",
        entity_id=test_suite.id,
        event_type="TEST_SUITE_CREATED",
    )
    db.commit()
    db.refresh(test_suite)
    return test_suite


@router.get("/test-suites/{suite_id}", response_model=TestSuiteRead)
def get_test_suite(suite_id: str, db: DbSession) -> TestSuite:
    return get_test_suite_or_404(db, suite_id)


@router.put("/test-suites/{suite_id}", response_model=TestSuiteRead)
def update_test_suite(
    suite_id: str,
    payload: TestSuiteUpdate,
    db: DbSession,
) -> TestSuite:
    test_suite = get_test_suite_or_404(db, suite_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(test_suite, field, value)

    write_audit_log(
        db,
        project_id=test_suite.project_id,
        entity_type="test_suite",
        entity_id=test_suite.id,
        event_type="TEST_SUITE_UPDATED",
        metadata={"updated_fields": sorted(updates)},
    )
    db.commit()
    db.refresh(test_suite)
    return test_suite


@router.delete("/test-suites/{suite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_suite(suite_id: str, db: DbSession) -> Response:
    test_suite = get_test_suite_or_404(db, suite_id)
    db.delete(test_suite)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
