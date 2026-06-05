# Services/audit_store.py
# In-memory store for mock/testing. Upgrade to Redis/DB for Cloud Run prod.
from typing import Dict

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