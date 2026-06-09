# Services/audit_store.py
# In-memory store for mock/testing. Upgrade to Redis/DB for Cloud Run prod.
from typing import Dict
from enum import Enum

class Checkpoint(str, Enum):
    FILE_RECEIVED       = "file_received"
    FILE_SAVED          = "file_saved"
    FILENAME_VALIDATED  = "filename_validated"
    HEADERS_VALIDATED   = "headers_validated"
    BATCH_REGISTERED    = "batch_registered"
    ROWS_VALIDATED      = "rows_validated"
    META_PAYLOAD_CREATED    = "meta_payload_created"
    META_DISPATCH_STARTED   = "meta_dispatch_started"
    META_DISPATCH_COMPLETED = "meta_dispatch_completed"
    GOOGLE_PAYLOAD_CREATED    = "google_payload_created"
    GOOGLE_DISPATCH_STARTED   = "google_dispatch_started"
    GOOGLE_DISPATCH_COMPLETED = "google_dispatch_completed"

_audit_store: Dict[str, dict] = {}       # request_id → audit record
_batch_registry: Dict[str, str] = {}     # "account_batchID" → request_id

def batch_key(account: str, batch_id: str) -> str:
    return f"{account}_{batch_id}"

def is_duplicate_batch(account: str, batch_id: str) -> bool:
    return batch_key(account, batch_id) in _batch_registry

def register_batch(account: str, batch_id: str, request_id: str):
    _batch_registry[batch_key(account, batch_id)] = request_id

def write_audit(request_id: str, record: dict):
    _audit_store[request_id] = record

def get_audit(request_id: str) -> dict | None:
    return _audit_store.get(request_id)

def checkpoint(request_id: str, stage: str, details: dict | None = None):
    record = _audit_store.get(request_id)

    if not record:
        record = {"checkpoints": []}
        _audit_store[request_id] = record

    record.setdefault("checkpoints", []).append({
        "stage": stage,
        "details": details or {}
    })