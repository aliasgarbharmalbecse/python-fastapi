from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class LeaveRequestCreate(BaseModel):
    user_id: UUID
    leave_type: UUID
    application_date: datetime
    leave_from: datetime
    leave_to: datetime
    leave_reason: str = Field(..., max_length=255)

class LeaveApprovalUpdate(BaseModel):
    approver_id: UUID
    comments: Optional[str] = Field(None, max_length=40)

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

    class Config:
        orm_mode = True
