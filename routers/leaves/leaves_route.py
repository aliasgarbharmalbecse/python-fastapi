from typing import List, Optional

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
@router.post("/request", response_model=LeaveRequestOut)
@register_permission('create_leave_request')
def submit_leave_request(
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
    print(leave_balance)
    if not leave_balance or leave_balance.leave_available - leave_balance.leave_taken < leave_days:
        raise HTTPException(status_code=404, detail="Leave balance not sufficient for the given leave type")

    submit_request = leave_repo.create_leave_request(request)

    #update leave balance
    leave_balance.leave_available -= leave_days
    db.commit()

    return submit_request
