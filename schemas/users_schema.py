from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, UUID4
import uuid

from typing_extensions import ClassVar


# ---------------- Role Schemas ----------------
class RoleBase(BaseModel):
    name: str
    hierarchy_level: int = Field(default=99, description="Lower number = higher in hierarchy")
    can_cross_departments: bool = Field(default=False, description="Can this role cross departments?")


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    id: UUID4


class RoleResponse(RoleBase):
    id: UUID4
    permissions: Optional[List[UUID4]] = None  # List of permission IDs

    class Config:
        from_attributes = True


# ---------------- Permission Schemas ----------------
class PermissionBase(BaseModel):
    name: str


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: UUID4
    roles: Optional[List[UUID4]] = None  # List of role IDs

    class Config:
        from_attributes = True

    json_schema_extra: ClassVar[dict] = {
        "example": {
            "id": "0c21ac9e-0301-4617-a6a0-00f8f0f45652",
            "name": "manager",
        }
    }


# ---------------- User Schemas ----------------
class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: Optional[str] = None
    department_name: str = None
    reports_to: Optional[UUID4] = None  # Manager ID


class UserCreate(UserBase):
    password: str
    roles: List[UUID4]  # Accepts list of Role IDs


class UserUpdate(UserBase):
    is_active: Optional[bool] = None
    password: Optional[str] = None
    roles: Optional[List[UUID4]] = None
    department_name: Optional[str] = None


class UserResponse(UserBase):
    id: UUID4
    roles: Optional[List[dict]] = None
    permissions: Optional[List[str]] = None  # List of permission names
    department: dict
    timezone: Optional[str] = None
    class Config:
        from_attributes = True  # Allows SQLAlchemy objects to be converted


class UserValidateResponse(UserResponse):
    hashed_password: str


# User Role Assignment Schema
class UserRoleAssign(BaseModel):
    user_id: UUID4
    role_name: str


# ---------------- Permission Schemas ----------------
class RolePermissionAssign(BaseModel):
    role_id: UUID4
    permission_ids: List[UUID4]
