import uuid
from typing import Optional, ClassVar

from pydantic import BaseModel, Field, ConfigDict


class DepartmentRequest(BaseModel):
    department_name: str
    department_head: Optional[uuid.UUID] = Field(description="This is optional and can be skipped", default=None)

    model_config = ConfigDict(extra="forbid")  #Disallow extra fields

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "department_name": "Ecommerce",
            "department_head": "550e8400-e29b-41d4-a716-446655440000"
        }
    }


class DepartmentUpdateRequest(BaseModel):
    id: uuid.UUID
    department_name: Optional[str]
    department_head: Optional[uuid.UUID] = Field(description="This is optional and can be skipped", default=None)

    model_config = ConfigDict(extra="forbid")  #Disallow extra fields

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "id": "0c21ac9e-0301-4617-a6a0-00f8f0f45652",
            "department_name": "Ecommerce",
            "department_head": "550e8400-e29b-41d4-a716-446655440000"
        }
    }

class DepartmentResponse(BaseModel):
    id: uuid.UUID
    department_name: Optional[str]
    department_head: Optional[uuid.UUID]

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "id": "0c21ac9e-0301-4617-a6a0-00f8f0f45652",
            "department_name": "Ecommerce",
            "department_head": "550e8400-e29b-41d4-a716-446655440000",
        }
    }