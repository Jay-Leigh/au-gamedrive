# utils.py
import re
from exceptions import HashValidationError

SHA256_REGEX = re.compile(r"^[a-f0-9]{64}$")

REQUIRED_HASHED_FIELDS = ["em", "ph"]
REQUIRED_STRING_FIELDS = ["external_id", "event_name", "event_time"]

def validate_sha256(value: str) -> bool:
    return bool(SHA256_REGEX.match(value))


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