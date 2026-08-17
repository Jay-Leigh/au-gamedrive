# services/audit_logging.py
from typing import Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from db.database import SessionLocal
from db.models import BatchRegistration
from models.logging import CheckpointLog, CheckpointName as Checkpoint, CheckpointStatus, AuditLog

def is_duplicate_batch(account: str, batch_id: str) -> bool:
    db = SessionLocal()
    try:
        return db.query(BatchRegistration).filter_by(account=account, batch_id=batch_id).first() is not None
    finally:
        db.close()

def register_batch(account: str, batch_id: str, request_id: str) -> bool:
    db = SessionLocal()
    try:
        db.add(BatchRegistration(account=account, batch_id=batch_id, request_id=request_id))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
    finally:
        db.close()

def checkpoint(request_id: str, stage: Checkpoint, details: Optional[dict] = None):
    db = SessionLocal()
    try:
        db.add(CheckpointLog(request_id=request_id, checkpoint=stage.value, status=CheckpointStatus.SUCCESSFUL.value, raw_payload=details))
        db.commit()
    finally:
        db.close()

def write_audit(request_id: str, record: dict):
    db = SessionLocal()
    try:
        db.add(AuditLog(request_id=request_id, **record))
        db.commit()
    finally:
        db.close()

def get_audit(request_id: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        row = db.query(AuditLog).filter_by(request_id=request_id).first()
        if not row:
            return None
        return {
            c.name: (v.isoformat() if isinstance(v := getattr(row, c.name), datetime) else v)
            for c in row.__table__.columns
        }
    finally:
        db.close()

def get_checkpoints(request_id: str) -> list[dict]:
    db = SessionLocal()
    try:
        rows = db.query(CheckpointLog).filter_by(request_id=request_id).order_by(CheckpointLog.id).all()
        return [{"checkpoint": r.checkpoint, "status": r.status, "raw_payload": r.raw_payload} for r in rows]
    finally:
        db.close()


def reset_audit_state():
    """Test-only. Wipes audit tables between test runs."""
    db = SessionLocal()
    try:
        db.query(CheckpointLog).delete()
        db.query(AuditLog).delete()
        db.query(BatchRegistration).delete()
        db.commit()
    finally:
        db.close()