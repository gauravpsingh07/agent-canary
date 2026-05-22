from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import Project
from agent_canary.schemas import DemoSeedResponse, ProjectCreate, ProjectRead, ProjectUpdate
from agent_canary.services.audit import write_audit_log
from agent_canary.services.demo_seed import seed_demo_data

router = APIRouter(tags=["projects"])
DbSession = Annotated[Session, Depends(get_db)]


def get_project_or_404(db: Session, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: DbSession) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())).all())


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: DbSession) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    db.flush()
    write_audit_log(
        db,
        project_id=project.id,
        entity_type="project",
        entity_id=project.id,
        event_type="PROJECT_CREATED",
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: DbSession) -> Project:
    return get_project_or_404(db, project_id)


@router.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: DbSession,
) -> Project:
    project = get_project_or_404(db, project_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value)

    write_audit_log(
        db,
        project_id=project.id,
        entity_type="project",
        entity_id=project.id,
        event_type="PROJECT_UPDATED",
        metadata={"updated_fields": sorted(updates)},
    )
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: DbSession) -> Response:
    project = get_project_or_404(db, project_id)
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/projects/{project_id}/seed-demo-data", response_model=DemoSeedResponse)
def seed_project_demo_data(project_id: str, db: DbSession) -> DemoSeedResponse:
    project = get_project_or_404(db, project_id)
    suites_created, test_cases_created, total_suites, total_test_cases = seed_demo_data(db, project)
    db.commit()
    return DemoSeedResponse(
        project_id=project.id,
        suites_created=suites_created,
        test_cases_created=test_cases_created,
        total_suites=total_suites,
        total_test_cases=total_test_cases,
    )
