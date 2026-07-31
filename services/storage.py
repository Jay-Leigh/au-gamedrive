import csv
import io
import json
from datetime import datetime
from google.cloud import storage
from core.config import settings

_gcs_client = storage.Client()
_bucket = _gcs_client.bucket(settings.gcs_bucket_name)

def _dated_prefix() -> str:
    now = datetime.utcnow()
    return f"{now:%Y}/{now:%m}/{now:%d}"

def save_raw(request_id: str, filename: str, content: bytes) -> str:
    blob_path = f"audiences/raw/{_dated_prefix()}/{request_id}_{filename}"
    _bucket.blob(blob_path).upload_from_string(content)
    return blob_path

def save_processed_csv(request_id: str, platform: str, rows: list[dict]) -> str:
    blob_path = f"audiences/processed/{platform}/{_dated_prefix()}/{request_id}.csv"
    if not rows:
        return blob_path
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    _bucket.blob(blob_path).upload_from_string(buf.getvalue(), content_type="text/csv")
    return blob_path

def save_payload_json(request_id: str, platform: str, payload: dict | list) -> str:
    blob_path = f"audiences/payloads/{platform}/{_dated_prefix()}/{request_id}.json"
    _bucket.blob(blob_path).upload_from_string(json.dumps(payload, indent=2, default=str), content_type="application/json")
    return blob_path

def save_failed(request_id: str, filename: str, content: bytes) -> str:
    blob_path = f"audiences/failed/{_dated_prefix()}/{request_id}_{filename}"
    _bucket.blob(blob_path).upload_from_string(content)
    return blob_path