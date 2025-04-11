from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID


# -------------------------
# TimeLog Schemas
# -------------------------

class TimeLogBase(BaseModel):
    punch_in_time: Optional[datetime] = None
    punch_out_time: Optional[datetime] = None
    duration: Optional[int] = None  # in seconds


class TimeLogCreate(TimeLogBase):
    user_id: UUID


class TimeLogRead(TimeLogBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True


# -------------------------
# TimeSummary Schemas
# -------------------------

class TimeSummaryBase(BaseModel):
    date: date
    overtime_seconds: Optional[int] = None
    actual_seconds: Optional[int] = None
    min_seconds: Optional[int] = None
    day_start_time: Optional[datetime] = None
    day_end_time: Optional[datetime] = None


class TimeSummaryCreate(TimeSummaryBase):
    user_id: UUID


class TimeSummaryRead(TimeSummaryBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
