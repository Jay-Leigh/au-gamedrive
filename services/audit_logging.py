# Services/audit_store.py
# In-memory store for mock/testing. Upgrade to Redis/DB for Cloud Run prod.
from typing import Dict
from enum import Enum

class Checkpoint(str, Enum):
    FILE_RECEIVED       = "file_received"
    FILENAME_VALIDATED  = "filename_validated"
    HEADERS_VALIDATED   = "headers_validated"
    FILE_SAVED          = "file_saved"
    BATCH_REGISTERED    = "batch_registered"
    ROWS_VALIDATED      = "rows_validated"
    PAYLOAD_CREATED     = "payload_created"
    DISPATCH_STARTED    = "dispatch_started"
    DISPATCH_COMPLETED  = "dispatch_completed"

_audit_store: Dict[str, dict] = {}       # request_id → audit record
_batch_registry: Dict[str, str] = {}     # "account_batchID" → request_id

def batch_key(account: str, audience_name: str, platform: str, date: str, batch_id: str) -> str:
    return f"{account}_{audience_name}_{platform}_{date}_{batch_id}"

def is_duplicate_batch(account: str, audience_name: str, platform: str, date: str, batch_id: str) -> bool:
    return batch_key(account, audience_name, platform, date, batch_id) in _batch_registry

def register_batch(account: str, audience_name: str, platform: str, date: str, batch_id: str, request_id: str):
    _batch_registry[batch_key(account, audience_name, platform, date, batch_id)] = request_id

def write_audit(request_id: str, record: dict):
    _audit_store[request_id] = record

def get_audit(request_id: str) -> dict | None:
    return _audit_store.get(request_id)

def get_checkpoints(request_id: str) -> list:
    record = _audit_store.get(request_id)
    return record.get("checkpoints", []) if record else []

def checkpoint(request_id: str, stage: str, details: dict | None = None):
    record = _audit_store.get(request_id)

    if not record:
        record = {"checkpoints": []}
        _audit_store[request_id] = record

    record.setdefault("checkpoints", []).append({
        "checkpoint": stage,
        "details": details or {}
    })

def reset_audit_state():
    """Test-only helper. Clears in-memory stores between test runs."""
    _audit_store.clear()
    _batch_registry.clear()