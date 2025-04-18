import uuid
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class LeaveStatusEnum(str, Enum):
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"
    pending = "pending"

class LeaveRequestCreate(BaseModel):
    user_id: UUID
    leave_type: UUID
    application_date: datetime
    leave_from: datetime
    leave_to: datetime
    leave_reason: str = Field(..., max_length=255)

class LeaveApprovalUpdate(BaseModel):
    leave_id: UUID
    status: LeaveStatusEnum
    comments: Optional[str] = Field(None, max_length=40)

    model_config = {
        "from_attributes": True
    }

class LeaveRequestOut(BaseModel):
    id: UUID
    user_id: UUID
    leave_type: UUID
    application_date: datetime
    leave_from: datetime
    leave_to: datetime
    leave_reason: str
    leave_status: str
    approved_date: Optional[datetime]
    approver_comments: Optional[str]
    approver_id: Optional[UUID]

    model_config = {
        "from_attributes": True
    }

class LeaveBalanceResponse(BaseModel):
    leave_type: str
    user_id: UUID
    user_name: str
    leave_available: int
    leave_taken: int
    leave_requested: int

    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    id: UUID
    firstname: str
    lastname: str

    model_config = {
        "from_attributes": True
    }


class LeaveTypeInfo(BaseModel):
    id: UUID
    title: str

    model_config = {
        "from_attributes": True
    }


class LeaveRequestsListResponse(BaseModel):
    id: UUID
    user: UserInfo
    leave_type_obj: LeaveTypeInfo
    application_date: datetime
    leave_from: datetime
    leave_to: datetime
    leave_reason: str
    leave_status: str
    approved_date: Optional[datetime]
    approver_comments: Optional[str]
    approver_id: Optional[UUID]

    model_config = {
        "from_attributes": True
    }

class PaginatedLeaveRequestsResponse(BaseModel):
    total_records: int
    page: int
    limit: int
    results: List[LeaveRequestsListResponse]

class LeaveTypeResponse(BaseModel):
    id: uuid.UUID
    title: str
    carry_forward: bool

    model_config = {
        "from_attributes": True
    }