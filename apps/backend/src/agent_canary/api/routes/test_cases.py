from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import TestCase, TestSuite
from agent_canary.schemas import TestCaseCreate, TestCaseRead, TestCaseUpdate
from agent_canary.services.audit import write_audit_log

router = APIRouter(tags=["test cases"])
DbSession = Annotated[Session, Depends(get_db)]


def get_test_suite_or_404(db: Session, suite_id: str) -> TestSuite:
    test_suite = db.get(TestSuite, suite_id)
    if test_suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test suite not found")
    return test_suite


def get_test_case_or_404(db: Session, test_case_id: str) -> TestCase:
    test_case = db.get(TestCase, test_case_id)
    if test_case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    return test_case


@router.get("/test-suites/{suite_id}/test-cases", response_model=list[TestCaseRead])
def list_test_cases(suite_id: str, db: DbSession) -> list[TestCase]:
    get_test_suite_or_404(db, suite_id)
    statement = (
        select(TestCase).where(TestCase.suite_id == suite_id).order_by(TestCase.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.post(
    "/test-suites/{suite_id}/test-cases",
    response_model=TestCaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_test_case(
    suite_id: str,
    payload: TestCaseCreate,
    db: DbSession,
) -> TestCase:
    test_suite = get_test_suite_or_404(db, suite_id)
    test_case = TestCase(suite_id=test_suite.id, **payload.model_dump())
    db.add(test_case)
    db.flush()
    write_audit_log(
        db,
        project_id=test_suite.project_id,
        entity_type="test_case",
        entity_id=test_case.id,
        event_type="TEST_CASE_CREATED",
        metadata={"suite_id": test_suite.id},
    )
    db.commit()
    db.refresh(test_case)
    return test_case


@router.get("/test-cases/{test_case_id}", response_model=TestCaseRead)
def get_test_case(test_case_id: str, db: DbSession) -> TestCase:
    return get_test_case_or_404(db, test_case_id)


@router.put("/test-cases/{test_case_id}", response_model=TestCaseRead)
def update_test_case(
    test_case_id: str,
    payload: TestCaseUpdate,
    db: DbSession,
) -> TestCase:
    test_case = get_test_case_or_404(db, test_case_id)
    test_suite = get_test_suite_or_404(db, test_case.suite_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(test_case, field, value)

    write_audit_log(
        db,
        project_id=test_suite.project_id,
        entity_type="test_case",
        entity_id=test_case.id,
        event_type="TEST_CASE_UPDATED",
        metadata={"suite_id": test_suite.id, "updated_fields": sorted(updates)},
    )
    db.commit()
    db.refresh(test_case)
    return test_case


@router.delete("/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(test_case_id: str, db: DbSession) -> Response:
    test_case = get_test_case_or_404(db, test_case_id)
    db.delete(test_case)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
