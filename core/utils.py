# utils.py
import re, csv, io
from exceptions import HashValidationError

SHA256_REGEX = re.compile(r"^[a-f0-9]{64}$")

REQUIRED_HASHED_FIELDS = ["em", "ph"]
REQUIRED_STRING_FIELDS = ["external_id", "event_name", "event_time"]

def validate_sha256(value: str) -> bool:
    return bool(SHA256_REGEX.match(value))

def validate_identifier_rows(csv_content: str) -> tuple[list[dict], list[dict], int]:
    """
    Generic identifier presence/format validation, shared across all platforms.
    Row rejected only if every REQUIRED_HASHED_FIELDS entry is missing, or a
    present field fails SHA-256 format. Platform-specific naming (em/ph ->
    EMAIL/PHONE, hashed_email/hashed_phone_number, etc.) is applied downstream
    by each platform's own transform step, not here.
    Returns (valid_rows, invalid_rows, missing_email_count).
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    valid_rows, invalid_rows, missing_email_count = [], [], 0
    for index, row in enumerate(reader):
        values = {field: row.get(field) for field in REQUIRED_HASHED_FIELDS}
        if not any(values.values()):
            invalid_rows.append({"row_index": index, "field": "/".join(REQUIRED_HASHED_FIELDS), "reason": "At least one identifier required"})
            continue
        row_valid = True
        for field, val in values.items():
            if val and not validate_sha256(val):
                invalid_rows.append({"row_index": index, "field": field, "reason": "Invalid SHA-256 hash"})
                row_valid = False
                break
        if not row_valid:
            continue
        if not values.get("em"):
            missing_email_count += 1
        valid_rows.append(row)
    return valid_rows, invalid_rows, missing_email_count

def spot_check_rows(sample_rows: list[dict]) -> None:
    """
    Validates the first 5 rows for correct SHA-256 hashing.
    Raises HTTPException on first failure.
    """
    for index, row in enumerate(sample_rows):
        for field in REQUIRED_HASHED_FIELDS:
            if field in row and not validate_sha256(row[field]):
                raise HashValidationError(f"Row {index + 1}: '{field}' is not a valid SHA-256 hash"
                )