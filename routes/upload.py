import csv
import io
import uuid
import logging
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi import status
from core.auth import verify_token

from core.config import settings
from core.auth import verify_token
from exceptions import (
    SchemaValidationError,
    HashValidationError,
    DuplicateBatchError,
    EmptyFileError,
    PlatformNotImplementedError,
)
from services.file_validation import validate_filename
from services.audience_processing import process_meta_upload
from services.google_ads_processing import process_google_ads_upload
from services.audit_logging import is_duplicate_batch, register_batch, checkpoint, Checkpoint
from services.storage import save_raw

router = APIRouter()

@router.post("/upload")
async def upload_audience(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(verify_token),
):
    request_id = str(uuid.uuid4()) ## can change name to job_id
    checkpoint(request_id, Checkpoint.FILE_RECEIVED, {"filename": file.filename})

    # Step 1: Validate Filename (raises FilenameValidationError)
    routing_metadata = validate_filename(file.filename)
    checkpoint(request_id, Checkpoint.FILENAME_VALIDATED, {"filename": file.filename})

    # Step 2: Duplicate batchID check
    if is_duplicate_batch(routing_metadata.account, routing_metadata.batch_id):
        raise DuplicateBatchError(
            f"Duplicate batchID '{routing_metadata.batch_id}' for account '{routing_metadata.account}'. Already processed."
        )

    # Step 3: Read + validate headers
    content = await file.read()
    if len(content) == 0:
        raise EmptyFileError("Uploaded file is empty")

    csv_str = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(csv_str))

    parsed_headers = reader.fieldnames or []
    required_headers = ["em", "ph", "external_id", "event_name", "event_time"]
    for field in required_headers:
        if field not in parsed_headers:
            raise SchemaValidationError(f"Missing required column: {field}")

    checkpoint(request_id, Checkpoint.HEADERS_VALIDATED, {"headers": parsed_headers})

    # Step 4: Save raw file (only after validation passes)
    raw_path = save_raw(file.filename, content)
    checkpoint(request_id, Checkpoint.FILE_SAVED, {"path": raw_path})

    # Step 5: Spot-check first 5 rows (raises HashValidationError)
    sample_rows = []
    for _ in range(5):
        try:
            sample_rows.append(next(reader))
        except StopIteration:
            break

    for index, row in enumerate(sample_rows):
        for field in ["em", "ph"]:
            val = row.get(field)
            if val and not settings.sha256_regex.match(val):
                raise HashValidationError(
                    f"Row {index+1}: {field} is not a valid SHA-256 hash"
                )

    # Register + hand off
    register_batch(routing_metadata.account, routing_metadata.batch_id, request_id)
    checkpoint(request_id, Checkpoint.BATCH_REGISTERED, {"batch_id": routing_metadata.batch_id})
    total_rows = max(len(csv_str.splitlines()) - 1, 0)

    if routing_metadata.platform == "meta":
        background_tasks.add_task(process_meta_upload, request_id, csv_str, routing_metadata)
    elif routing_metadata.platform == "googleads":
        background_tasks.add_task(process_google_ads_upload, request_id, csv_str, routing_metadata)
    else:
        raise PlatformNotImplementedError(
            f"Platform '{routing_metadata.platform}' not yet implemented"
        )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"request_id": request_id, "status": "processing", "rows_received": total_rows},
    )
