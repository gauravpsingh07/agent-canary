from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TestSuiteBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    category: str = Field(default="general", min_length=1, max_length=80)


class TestSuiteCreate(TestSuiteBase):
    pass


class TestSuiteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)


class TestSuiteRead(TestSuiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

