from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Table, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime
from typing import List, Optional
from configurations.database import Base


class TimeLog(Base):
    __tablename__ = "time_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    punch_in_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    punch_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Duration in seconds


class TimeSummary(Base):
    __tablename__ = "time_summary"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    date: Mapped[Date] = mapped_column(Date, default=datetime.utcnow)
    overtime_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Duration in seconds
    actual_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Duration in seconds
    min_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Duration in seconds
    day_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    day_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

