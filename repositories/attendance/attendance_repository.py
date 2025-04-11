import uuid
from datetime import datetime, date
from typing import Optional, Any, Type, List

from sqlalchemy.orm import Session
from models.attendance_model import TimeLog, TimeSummary
from schemas.attendance_schema import TimeLogRead, TimeSummaryRead, TimeLogCreate, TimeSummaryCreate

class AttendanceRepository:

    def __init__(self, db: Session):
        self.db = db

    def check_if_time_log_exists(self, user_id: uuid.UUID) -> Optional[Type[TimeLog]]:
        existing_log = self.db.query(TimeLog).filter(
            TimeLog.user_id == user_id,
            TimeLog.punch_out_time.is_(None)
        ).order_by(TimeLog.punch_in_time.desc()).first()
        return existing_log or None

    def create_time_log(self, time_log_data: TimeLogCreate) -> TimeLogRead:
        new_time_log = TimeLog(**time_log_data.dict())
        self.db.add(new_time_log)
        self.db.commit()
        self.db.refresh(new_time_log)
        return TimeLogRead(
            id=new_time_log.id,
            user_id=new_time_log.user_id,
            punch_in_time=new_time_log.punch_in_time,
            punch_out_time=new_time_log.punch_out_time,
            duration=new_time_log.duration
        )

    def get_time_logs_for_date(self, user_id: str, target_date: date):
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())

        return self.db.query(TimeLog).filter(
            TimeLog.user_id == user_id,
            TimeLog.punch_in_time >= start,
            TimeLog.punch_in_time <= end
        ).all()

    def create_time_summary(self, time_summary_data: TimeSummaryCreate) -> TimeSummaryRead:
        new_time_summary = TimeSummary(**time_summary_data.dict())
        self.db.add(new_time_summary)
        self.db.commit()
        self.db.refresh(new_time_summary)
        return TimeSummaryRead (
            id=new_time_summary.id,
            user_id=new_time_summary.user_id,
            date=new_time_summary.date,
            overtime_seconds=new_time_summary.overtime_seconds,
            actual_seconds=new_time_summary.actual_seconds,
            min_seconds=new_time_summary.min_seconds,
            day_start_time=new_time_summary.day_start_time,
            day_end_time=new_time_summary.day_end_time
        )

    def check_summary_exists_for_date(self, user_id: str, target_date: date) -> bool:
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())

        time_summary = self.db.query(TimeSummary).filter(
            TimeSummary.user_id == user_id,
            TimeSummary.date >= start,
            TimeSummary.date <= end
        ).first()

        return time_summary is not None

    def get_time_logs_for_range(self, user_id: str, start: datetime, end: datetime):
        return self.db.query(TimeLog).filter(
            TimeLog.user_id == user_id,
            TimeLog.punch_in_time >= start,
            TimeLog.punch_in_time <= end
        ).all()