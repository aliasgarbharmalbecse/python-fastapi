from http.cookiejar import user_domain_match
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from configurations.database import get_db
from schemas.leave_schema import LeaveRequestCreate, LeaveRequestOut, LeaveApprovalUpdate
from models.user_model import User
from repositories.users.users_repository import UserRepository
from utilities.permission_utlis import enforce_permissions_dependency, register_permission
from utilities.time_utils import calculate_days, get_current_quarter
from repositories.leaves.leave_repository import LeaveRepository
from dotenv import load_dotenv
import os
import pytz

router = APIRouter(
    prefix="/leave",
    tags=["Leave Management"]
)

# Submit a leave request
@router.post("/request/{user_id}", response_model=LeaveRequestOut)
@register_permission('create_leave_request')
def submit_leave_request(
        user_id: UUID,
        request: LeaveRequestCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    current_quarter = get_current_quarter(request.application_date)
    year = request.application_date.year
    leave_days = calculate_days(request.leave_from, request.leave_to)
    leave_repo = LeaveRepository(db)

    ##verify if current user = user id (applying for self) if not, check if the current_user has access to below user


    #check if overlaping leaves
    if leave_repo.check_overlapping_leave(request):
        raise HTTPException(status_code=400, detail="Overlapping leave request exists.")

    #check leave balance
    leave_balance = leave_repo.get_leave_balance(request, year, current_quarter)
    if not leave_balance or leave_balance.leave_available - leave_balance.leave_taken < leave_days:
        raise HTTPException(status_code=404, detail="Leave balance not sufficient for the given leave type")

    submit_request = leave_repo.create_leave_request(request)

    #update leave balance
    leave_balance.leave_available -= leave_days
    leave_balance.leave_requested += leave_days
    db.commit()

    return submit_request

@router.put('/update/{user_id}', response_model=LeaveRequestOut)
@register_permission('leave_status_updates')
def update_leave(
    user_id: UUID,
    request: LeaveApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(enforce_permissions_dependency)
):
    approver_id = current_user.get("sub")
    leave_repo = LeaveRepository(db)

    # Fetch and update leave in one go
    leave_update = leave_repo.process_leave_update(user_id, request, approver_id)
    leave = leave_update[0]
    original_status = leave_update[1]
    # Calculate leave balance update
    current_quarter = get_current_quarter(leave.application_date)
    year = leave.application_date.year
    leave_days = calculate_days(leave.leave_from, leave.leave_to)

    if not leave_repo.update_leave_balance(leave, original_status, year, current_quarter, leave_days):
        raise HTTPException(status_code=500, detail="Failed to update leave balance.")

    return LeaveRequestOut.model_validate(leave)