import json
import csv
import io
from pathlib import Path

BUCKET = Path("storage_bucket")
RAW       = BUCKET / "raw"
PROCESSED = BUCKET / "processed"
PAYLOADS  = BUCKET / "payloads"
FAILED    = BUCKET / "failed"
AUDIT     = BUCKET / "audit"

for _d in [RAW, PROCESSED/"meta", PROCESSED/"google",
           PAYLOADS/"meta", PAYLOADS/"google", FAILED, AUDIT]:
    _d.mkdir(parents=True, exist_ok=True)


def save_raw(filename: str, content: bytes) -> str:
    path = RAW / filename
    path.write_bytes(content)
    return str(path)


def save_processed_csv(request_id: str, platform: str, rows: list[dict]) -> str:
    path = PROCESSED / platform / f"{request_id}.csv"
    if rows:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    return str(path)


def save_payload_json(request_id: str, platform: str, payload: dict | list) -> str:
    path = PAYLOADS / platform / f"{request_id}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))
    return str(path)


def save_failed(filename: str, content: bytes) -> str:
    path = FAILED / filename
    path.write_bytes(content)
    return str(path)