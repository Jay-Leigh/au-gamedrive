# models/logging.py
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer, String, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from helpers.db import Base


class CheckpointStatus(str, Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    SKIPPED = "skipped"


class CheckpointName(str, Enum):
    FILE_RECEIVED = "file_received"
    FILENAME_VALIDATED = "filename_validated"
    FILE_SAVED = "file_saved"
    HEADERS_VALIDATED = "headers_validated"
    ROWS_VALIDATED = "rows_validated"
    BATCH_REGISTERED = "batch_registered"
    PAYLOAD_CREATED = "payload_created"
    DISPATCH_STARTED = "dispatch_started"
    DISPATCH_COMPLETED = "dispatch_completed"


class OverallStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL_FAILURE = "partial_failure"
    FAILED = "failed"


# --- SQLAlchemy DB Models ---

class CheckpointLog(Base):
    __tablename__ = "checkpoint_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    checkpoint: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    source_system: Mapped[str] = mapped_column(String(30), nullable=False, default="audience_uploader")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    account: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    audience_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    source_system: Mapped[str] = mapped_column(String(30), nullable=False, default="audience_uploader")
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_rows: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    dispatched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    succeeded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    overall_status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# --- Pydantic Schemas ---

class CheckpointLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: str
    checkpoint: str
    status: str
    raw_payload: Optional[dict] = None
    source_system: str
    created_at: datetime


class AuditLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: str
    filename: str
    account: str
    platform: str
    source_system: str
    total_rows: int
    valid_rows: int
    invalid_rows: Optional[list] = None
    dispatched: int
    succeeded: int
    failed: Optional[list] = None
    overall_status: str
    created_at: datetime