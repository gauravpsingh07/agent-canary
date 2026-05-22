from pydantic import BaseModel


class DemoSeedResponse(BaseModel):
    project_id: str
    suites_created: int
    test_cases_created: int
    total_suites: int
    total_test_cases: int

