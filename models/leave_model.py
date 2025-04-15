from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Table, DateTime, Nullable, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column, foreign
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from configurations.database import Base

class LeaveType(Base):

    __tablename__ = 'leave_type'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, unique=True)
    carry_forward: Mapped[bool] = mapped_column(Boolean, default=False)

class LeaveBalance(Base):

    __tablename__ = 'leave_balance'

    __table_args__ = (
        UniqueConstraint('user_id', 'leave_type', 'year', 'quarter', name='uq_leave_balance_period'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    leave_type: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leave_type.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    leave_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    leave_taken: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=None, nullable=True)

class LeaveRequests(Base):

    __tablename__ = "leave_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    leave_type: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leave_type.id", ondelete="CASCADE"))
    application_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    leave_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    leave_to: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    leave_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    leave_status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING")
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None, nullable=True)
    approver_comments: Mapped[str] = mapped_column(String(40), default=None, nullable=True)
    approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True),
                                                             ForeignKey("users.id", ondelete="SET NULL"), default=None, nullable=True)
