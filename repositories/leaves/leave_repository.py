import uuid
from calendar import leapdays

from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.leave_schema import LeaveRequestCreate, LeaveRequestOut, LeaveApprovalUpdate
from models.user_model import User
from models.leave_model import LeaveRequests, LeaveType, LeaveBalance


class LeaveRepository:

    def __init__(self, db: Session):
        self.db = db

    def check_overlapping_leave(self, request: LeaveRequestCreate) -> bool:
        # Check for overlapping leave requests
        overlapping = self.db.query(LeaveRequests).filter(
            LeaveRequests.user_id == request.user_id,
            LeaveRequests.leave_from <= request.leave_to,
            LeaveRequests.leave_to >= request.leave_from
        ).first()
        if overlapping:
            return True
        return False

    def get_leave_balance(self, request: LeaveRequestCreate, year, quarter):
        leave_balance = self.db.query(LeaveBalance).filter_by(
            user_id=request.user_id,
            leave_type=request.leave_type,
            year=year,
            quarter=quarter
        ).first()

        return leave_balance

    def create_leave_request(self, request):
        leave_request = LeaveRequests(**request.dict())
        self.db.add(leave_request)
        self.db.commit()
        self.db.refresh(leave_request)

        return LeaveRequestOut(
            id=leave_request.id,
            user_id=leave_request.user_id,
            leave_type=leave_request.leave_type,
            application_date=leave_request.application_date,
            leave_from=leave_request.leave_from,
            leave_to=leave_request.leave_to,
            leave_status=leave_request.leave_status,
            leave_reason=leave_request.leave_reason,
            approved_date=leave_request.approved_date,
            approver_id=leave_request.approver_id,
            approver_comments=leave_request.approver_comments
        )
