import uuid
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, UUID4
from datetime import datetime


# ---------------- Department Schemas ----------------
class DepartmentBase(BaseModel):
    department_name: str
    department_head: Optional[UUID4] = Field(
        default=None, description="Optional, represents the user ID of the department head"
    )


class DepartmentCreate(DepartmentBase):
    json_schema_extra: ClassVar[dict] = {
        "example": {
            "department_name": "Ecommerce",
            "department_head": "550e8400-e29b-41d4-a716-446655440000"  # Example UUID
        }
    }
    pass


class DepartmentUpdate(BaseModel):
    id: UUID4
    department_name: Optional[str] = None
    department_head: Optional[UUID4] = Field(
        default=None, description="Optional, represents the user ID of the department head"
    )

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "id": "0c21ac9e-0301-4617-a6a0-00f8f0f45652",
            "department_name": "Ecommerce",
            "department_head": "550e8400-e29b-41d4-a716-446655440000",
        }
    }


class DepartmentResponse(DepartmentBase):
    id: UUID4
    created_at: datetime

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "id": "0c21ac9e-0301-4617-a6a0-00f8f0f45652",
            "department_name": "Ecommerce",
            "department_head": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": "2025-04-04T10:00:00Z",
        }
    }

    class Config:
        from_attributes = True  # Ensures SQLAlchemy model conversion
