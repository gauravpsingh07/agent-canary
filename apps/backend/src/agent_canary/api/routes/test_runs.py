from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import SessionLocal, get_db
from agent_canary.models import TestCase, TestRun, TestRunStep, TestSuite
from agent_canary.models.base import utc_now
from agent_canary.schemas import SuiteRunResponse, TestRunRead, TestRunStepRead
from agent_canary.services.audit import write_audit_log
from agent_canary.workflows.evaluation import run_test_case_workflow

router = APIRouter(tags=["test runs"])
DbSession = Annotated[Session, Depends(get_db)]


def get_test_case_or_404(db: Session, test_case_id: str) -> TestCase:
    test_case = db.get(TestCase, test_case_id)
    if test_case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    return test_case


def get_test_suite_or_404(db: Session, suite_id: str) -> TestSuite:
    test_suite = db.get(TestSuite, suite_id)
    if test_suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test suite not found")
    return test_suite


def get_test_run_or_404(db: Session, test_run_id: str) -> TestRun:
    test_run = db.get(TestRun, test_run_id)
    if test_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test run not found")
    return test_run


def _run_test_case_in_background(test_case_id: str) -> None:
    session = SessionLocal()
    try:
        run_test_case_workflow(session, test_case_id)
    finally:
        session.close()


@router.post("/test-cases/{test_case_id}/run", response_model=TestRunRead)
def run_test_case(test_case_id: str, db: DbSession) -> TestRun:
    get_test_case_or_404(db, test_case_id)
    return run_test_case_workflow(db, test_case_id)


@router.post("/test-suites/{suite_id}/run", response_model=SuiteRunResponse)
def run_test_suite(
    suite_id: str,
    db: DbSession,
    background_tasks: BackgroundTasks,
    async_mode: bool = Query(default=False),
) -> SuiteRunResponse:
    suite = get_test_suite_or_404(db, suite_id)
    statement = (
        select(TestCase)
        .where(TestCase.suite_id == suite_id)
        .order_by(TestCase.created_at.asc())
    )
    test_cases = list(db.scalars(statement).all())

    if async_mode:
        # Pre-create pending TestRun rows so callers can poll while jobs execute off-thread.
        run_ids: list[str] = []
        for test_case in test_cases:
            placeholder = TestRun(
                test_case_id=test_case.id,
                status="pending",
                started_at=utc_now(),
                run_metadata={"mode": "background"},
            )
            db.add(placeholder)
            db.flush()
            write_audit_log(
                db,
                project_id=suite.project_id,
                entity_type="test_run",
                entity_id=placeholder.id,
                event_type="TEST_RUN_QUEUED",
                metadata={"test_case_id": test_case.id, "suite_id": suite_id},
            )
            run_ids.append(placeholder.id)
        db.commit()
        for test_case in test_cases:
            background_tasks.add_task(_run_test_case_in_background, test_case.id)
        return SuiteRunResponse(suite_id=suite_id, test_run_ids=run_ids)

    test_run_ids = [run_test_case_workflow(db, test_case.id).id for test_case in test_cases]
    return SuiteRunResponse(suite_id=suite_id, test_run_ids=test_run_ids)


@router.get("/test-runs", response_model=list[TestRunRead])
def list_test_runs(db: DbSession) -> list[TestRun]:
    statement = select(TestRun).order_by(TestRun.created_at.desc())
    return list(db.scalars(statement).all())


@router.get("/test-runs/{test_run_id}", response_model=TestRunRead)
def get_test_run(test_run_id: str, db: DbSession) -> TestRun:
    return get_test_run_or_404(db, test_run_id)


@router.get("/test-runs/{test_run_id}/steps", response_model=list[TestRunStepRead])
def list_test_run_steps(test_run_id: str, db: DbSession) -> list[TestRunStep]:
    get_test_run_or_404(db, test_run_id)
    statement = (
        select(TestRunStep)
        .where(TestRunStep.test_run_id == test_run_id)
        .order_by(TestRunStep.step_order.asc())
    )
    return list(db.scalars(statement).all())
