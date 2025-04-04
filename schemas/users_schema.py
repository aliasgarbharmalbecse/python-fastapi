from typing import Optional, ClassVar, List

from pydantic import BaseModel, Field, ConfigDict, EmailStr, UUID4
import uuid


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    id: uuid.UUID

    model_config = ConfigDict(extra="forbid")  # Disallow extra fields

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "id": "0c21ac9e-0301-4617-a6a0-00f8f0f45652",
            "name": "manager",
        }
    }


# Base User Schema
class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: Optional[str] = None
    department_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    roles: List[str]  # Accepts role names, not IDs


class UserUpdate(UserBase):
    is_active: Optional[bool]
    password: Optional[str] = None
    roles: Optional[List[str]] = None


class UserResponse(UserBase):
    id: UUID4
    roles: Optional[List[dict]] = None
    hashed_password: Optional[str] = None

    class Config:
        from_attributes = True  # Allows SQLAlchemy objects to be converted


# User Role Assignment Schema
class UserRoleAssign(BaseModel):
    user_id: UUID4
    role_name: str
