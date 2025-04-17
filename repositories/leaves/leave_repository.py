import datetime
import uuid
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from schemas.leave_schema import LeaveRequestCreate, LeaveRequestOut, LeaveApprovalUpdate, LeaveStatusEnum, \
    LeaveBalanceResponse
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

    def process_leave_update(
            self,
            user_id: uuid.UUID,
            request: LeaveApprovalUpdate,
            approver_id: uuid.UUID
    )-> tuple[LeaveRequests, str]:
        leave_req = self.db.query(LeaveRequests).filter(LeaveRequests.id == request.leave_id).first()

        if not leave_req:
            raise HTTPException(status_code=404, detail="Leave record doesn't exist")

        if leave_req.leave_status == request.status:
            raise HTTPException(status_code=400, detail=f"Leave is already {request.status.value}")

        if leave_req.leave_status == LeaveStatusEnum.cancelled:
            raise HTTPException(400, "Cancelled leaves can't be processed")

        original_status = leave_req.leave_status

        leave_req.leave_status = request.status
        leave_req.approved_date = datetime.datetime.now(datetime.timezone.utc)
        leave_req.approver_comments = request.comments
        leave_req.approver_id = approver_id

        self.db.commit()
        self.db.refresh(leave_req)

        # Return both current and original status
        return [leave_req, original_status]

    def update_leave_balance(
            self,
            leave,
            original_status: str,
            year: int,
            current_quarter: int,
            days: int
    ) -> bool:
        try:
            leave_balance = self.get_leave_balance(leave, year, current_quarter)
            days = int(days)

            if leave.leave_status == LeaveStatusEnum.approved:
                leave_balance.leave_taken += days
                leave_balance.leave_requested -= days

            elif leave.leave_status == LeaveStatusEnum.rejected:
                leave_balance.leave_available += days
                leave_balance.leave_requested -= days

            elif leave.leave_status == LeaveStatusEnum.cancelled:
                if original_status == LeaveStatusEnum.approved:
                    leave_balance.leave_available += days
                    leave_balance.leave_taken -= days
                elif original_status == LeaveStatusEnum.pending:
                    leave_balance.leave_available += days
                    leave_balance.leave_requested -= days

            self.db.commit()
            return True

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

    def get_user_leave_balance(self, user_id: uuid.UUID, year: int, quarter: int):
        leave_balances = self.db.query(LeaveBalance).options(
            joinedload(LeaveBalance.leave_type_obj),
            joinedload(LeaveBalance.user)
        ).filter(
            LeaveBalance.user_id == user_id,
            LeaveBalance.year == year,
            LeaveBalance.quarter == quarter
        ).all()

        return [
            LeaveBalanceResponse(
                leave_type=lb.leave_type_obj.title,
                user_id=lb.user_id,
                user_name=f"{lb.user.firstname} {lb.user.lastname}",
                leave_available=lb.leave_available,
                leave_taken=lb.leave_taken,
                leave_requested=lb.leave_requested,
            )
            for lb in leave_balances
        ]

    def get_leave_requests(self, user_id: uuid.UUID, from_date: datetime, to_date: datetime):

        leave_requests = (
            self.db.query(LeaveRequests)
            .options(joinedload(LeaveRequests.user), joinedload(LeaveRequests.leave_type_obj))
            .filter(
                LeaveRequests.leave_from >= from_date,
                LeaveRequests.leave_to <= to_date,
                LeaveRequests.user_id == user_id
            )
            .all()
        )

        return leave_requests