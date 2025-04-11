from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from configurations.database import get_db
from models.user_model import User
from schemas.attendance_schema import TimeLogCreate, TimeSummaryRead, TimeLogRead, TimeSummaryCreate
from utilities.permission_utlis import enforce_permissions_dependency, register_permission
from repositories.attendance.attendance_repository import AttendanceRepository
from dotenv import load_dotenv
import os
import pytz

router = APIRouter(
    prefix="/timelog",
    tags=["Time Log"]
)


@router.post("/punch-in", response_model=TimeLogRead)
@register_permission('punch_in')
async def punch_in(
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    ###check if there is an open existing log. If yes, raise an error
    attendance_repo = AttendanceRepository(db)
    user_id = current_user.get('sub')
    existing_log = attendance_repo.check_if_time_log_exists(user_id)
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an open time log."
        )

    ###create a new time log
    time_log_data = TimeLogCreate(
        user_id=user_id,
        punch_in_time=datetime.utcnow()
    )

    return attendance_repo.create_time_log(time_log_data)


@router.post("/punch-out", response_model=TimeLogRead)
@register_permission('punch_out')
async def punch_out(
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    ###check if there is an open existing log. If no, raise an error
    attendance_repo = AttendanceRepository(db)
    user_id = current_user.get('sub')
    existing_log = attendance_repo.check_if_time_log_exists(user_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have an open time log."
        )
    ###update the existing time log with punch out time
    existing_log.punch_out_time = datetime.utcnow()
    existing_log.duration = (existing_log.punch_out_time - existing_log.punch_in_time).total_seconds()
    db.commit()
    db.refresh(existing_log)
    return TimeLogRead(
        id=existing_log.id,
        user_id=existing_log.user_id,
        punch_in_time=existing_log.punch_in_time,
        punch_out_time=existing_log.punch_out_time,
        duration=existing_log.duration
    )


@router.post("/day-end")
@register_permission('day_end')
async def day_end(
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    load_dotenv()
    min_hours = os.getenv("MIN_WORK_HOURS_PER_DAY") or "8"
    user_id = current_user.get("sub")
    user_timezone_str = current_user.get("timezone")
    user_tz = pytz.timezone(user_timezone_str)
    now_local = datetime.now(user_tz)

    # Define day start and end in user's local time
    start_local = user_tz.localize(datetime.combine(now_local.date(), time.min))
    end_local = user_tz.localize(datetime.combine(now_local.date(), time.max))

    # Convert to UTC for DB query
    start_utc = start_local.astimezone(pytz.utc)
    end_utc = end_local.astimezone(pytz.utc)

    attendance_repo = AttendanceRepository(db)

    # Close any open punch log

    # Fetch logs for the day
    logs = attendance_repo.get_time_logs_for_range(user_id, start_utc, end_utc)
    if not logs:
        raise HTTPException(status_code=404, detail="No punch logs found for today.")

    # First punch in and last punch out
    first_punch_in = min(log.punch_in_time for log in logs)
    last_punch_out = max((log.punch_out_time or datetime.utcnow()) for log in logs)

    # Total worked time
    actual_seconds = sum(log.duration or 0 for log in logs)
    min_seconds = int(min_hours) * 60 * 60
    overtime = max(0, actual_seconds - min_seconds)

    summary_date = now_local.date()

    # Check if summary already exists for the day
    existing_summary = attendance_repo.check_summary_exists_for_date(user_id, summary_date)

    if existing_summary:
        raise HTTPException(status_code=400, detail="Summary already exists for today.")

    summary = TimeSummaryCreate(
        user_id=user_id,
        date=summary_date,
        actual_seconds=actual_seconds,
        min_seconds=min_seconds,
        overtime_seconds=overtime,
        day_start_time=first_punch_in,
        day_end_time=last_punch_out
    )

    return attendance_repo.create_time_summary(summary)


@router.get("/user-logs", response_model=List[TimeLogRead])
@register_permission('view_time_logs')
async def get_user_time_logs(
        date_param: Optional[date] = Query(default=None, description="Filter by date (YYYY-MM-DD)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    user_id = current_user.get("sub")
    user_timezone_str = current_user.get("timezone")
    user_tz = pytz.timezone(user_timezone_str)

    # Determine date range in local time
    target_date = date_param or datetime.now(user_tz).date()
    start_local = user_tz.localize(datetime.combine(target_date, time.min))
    end_local = user_tz.localize(datetime.combine(target_date, time.max))

    # Convert to UTC for DB query
    start_utc = start_local.astimezone(pytz.utc)
    end_utc = end_local.astimezone(pytz.utc)

    attendance_repo = AttendanceRepository(db)
    logs = attendance_repo.get_time_logs_for_range(user_id, start_utc, end_utc)

    return logs
