from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from configurations.database import get_db
from schemas.leave_schema import LeaveRequestCreate, LeaveRequestOut, LeaveApprovalUpdate, LeaveBalanceResponse, \
    LeaveRequestsListResponse, LeaveTypeResponse
from models.user_model import User
from utilities.permission_utlis import enforce_permissions_dependency, register_permission
from utilities.time_utils import calculate_days, get_current_quarter
from repositories.leaves.leave_repository import LeaveRepository
import utilities.get_accessible_users as acc


router = APIRouter(
    prefix="/leave",
    tags=["Leave Management"]
)

@router.get('/leave_type', response_model=List[LeaveTypeResponse] ,status_code=status.HTTP_200_OK)
@register_permission('get_leaves_type')
def get_leave_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(enforce_permissions_dependency)
):
    leave_repo = LeaveRepository(db)
    return leave_repo.get_leave_types()

# Submit a leave request
@router.post("/request/{user_id}", response_model=LeaveRequestOut, status_code=status.HTTP_201_CREATED)
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


@router.put('/update/{user_id}', response_model=LeaveRequestOut, status_code=status.HTTP_201_CREATED)
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


@router.get(
    '/balanace/{user_id}/',
    response_model=List[LeaveBalanceResponse],
    status_code=status.HTTP_200_OK
)
@register_permission('get_leave_balance')
async def get_leave_balance(
    user_id: UUID,
    year: int = Query(None, description="Year to get leave balance. If not entered, current year will be taken"),
    quarter: int = Query(None, description="Quarter (1 to 4) to filter, If not entered, current quarter will be taken"),
    leave_type: Optional[UUID] = Query(None, description="Filter by leave type ID."),
    db: Session = Depends(get_db),
    current_user: User = Depends(enforce_permissions_dependency)
):
    now = datetime.now()
    year = year or now.year
    quarter = quarter or ((now.month - 1) // 3 + 1)

    leave_repo = LeaveRepository(db)
    leave_balance = leave_repo.get_user_leave_balance(user_id, year, quarter, leave_type)
    return leave_balance

@router.get('/request/{user_id}', response_model=list[LeaveRequestsListResponse], status_code=status.HTTP_200_OK)
@register_permission('view_leave_requests')
def get_user_leave_requests(
    user_id: UUID,
    from_date: date = Query(None, description="Enter from date in YYYY-MM-DD format. 1st Jan is default"),
    to_date: date = Query(None, description="Enter to date in YYYY-MM-DD format.  31st Dec is default"),
    db: Session = Depends(get_db),
    current_user: User = Depends(enforce_permissions_dependency)
):
    # Set default date range to current year if not provided
    current_year = datetime.now().year
    from_date = from_date or date(current_year, 1, 1)
    to_date = to_date or date(current_year, 12, 31)

    # Convert to datetime
    from_datetime = datetime.combine(from_date, datetime.min.time())
    to_datetime = datetime.combine(to_date, datetime.max.time())

    leave_repo = LeaveRepository(db)
    leave_requests = leave_repo.get_leave_requests(user_id, from_datetime, to_datetime)

    return leave_requests

@router.get('/requests', status_code=status.HTTP_200_OK)
@register_permission('users_leave_request_all')
async def get_users_leave_requests(
    from_date: Optional[date] = Query(None, description="Start date in YYYY-MM-DD format."),
    to_date: Optional[date] = Query(None, description="End date in YYYY-MM-DD format."),
    leave_status: Optional[str] = Query(None, description="Filter by leave status (e.g., PENDING, APPROVED, REJECTED)."),
    leave_type: Optional[UUID] = Query(None, description="Filter by leave type ID."),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(enforce_permissions_dependency)
):
    # Get accessible users
    accessible_users = acc.get_accessible_users(db, current_user)
    accessible_user_ids = [user.id for user in accessible_users]

    leave_repo = LeaveRepository(db)
    leave_requests = leave_repo.get_all_leave_requests(
        accessible_user_ids,
        from_date,
        to_date,
        leave_status,
        leave_type,
        limit,
        page
    )

    return leave_requests


# add api to create laeve request. Implement a feature of max carry forward feature
# add api to add leave balance and auto calculation logic
# manually add leaves for user.