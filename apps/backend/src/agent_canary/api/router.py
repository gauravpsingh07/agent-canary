from fastapi import APIRouter

from agent_canary.api.routes.approvals import router as approvals_router
from agent_canary.api.routes.audit import router as audit_router
from agent_canary.api.routes.evaluation import router as evaluation_router
from agent_canary.api.routes.health import router as health_router
from agent_canary.api.routes.llm_calls import router as llm_calls_router
from agent_canary.api.routes.policy import router as policy_router
from agent_canary.api.routes.projects import router as projects_router
from agent_canary.api.routes.rag import router as rag_router
from agent_canary.api.routes.test_cases import router as test_cases_router
from agent_canary.api.routes.test_runs import router as test_runs_router
from agent_canary.api.routes.test_suites import router as test_suites_router
from agent_canary.api.routes.tool_calls import router as tool_calls_router
from agent_canary.api.routes.tools import router as tools_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(projects_router)
api_router.include_router(test_suites_router)
api_router.include_router(test_cases_router)
api_router.include_router(test_runs_router)
api_router.include_router(tools_router)
api_router.include_router(policy_router)
api_router.include_router(evaluation_router)
api_router.include_router(approvals_router)
api_router.include_router(rag_router)
api_router.include_router(audit_router)
api_router.include_router(llm_calls_router)
api_router.include_router(tool_calls_router)
