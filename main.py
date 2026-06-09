import csv
import io
import uuid
import logging
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from Services.file_validation import validate_filename
from Services.audience_processing import process_meta_upload
from Services.google_ads_processing import process_google_ads_upload
from Services.audit_logging import is_duplicate_batch, register_batch, get_audit, checkpoint, Checkpoint
from Services.storage import save_raw


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Audience Uploader API")

_security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(_security)) -> str:
    if credentials.credentials != settings.system_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Routes
@app.post("/upload")
async def upload_audience(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    # Generate request_id first — needed for all checkpoints
    request_id = str(uuid.uuid4())
    checkpoint(request_id, Checkpoint.FILE_RECEIVED, {"filename": file.filename})

    # Step 1: Validate Filename
    routing_metadata = validate_filename(file.filename)
    checkpoint(request_id, Checkpoint.FILENAME_VALIDATED, {"filename": file.filename})

    # Step 2: Duplicate batchID check
    if is_duplicate_batch(routing_metadata.account, routing_metadata.batch_id):
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate batchID '{routing_metadata.batch_id}' for account '{routing_metadata.account}'. Already processed."
        )

    # Step 3: Read + save raw file
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    csv_str = content.decode("utf-8")
    raw_path = save_raw(file.filename, content)
    checkpoint(request_id, Checkpoint.FILE_SAVED, {"path": raw_path})
    reader = csv.DictReader(io.StringIO(csv_str))

    # Step 4: Header check
    parsed_headers = reader.fieldnames or []
    required_headers = ["em", "ph", "external_id", "event_name", "event_time"]
    for field in required_headers:
        if field not in parsed_headers:
            raise HTTPException(status_code=400, detail=f"Missing required column: {field}")
        
    checkpoint(request_id, Checkpoint.HEADERS_VALIDATED, {"headers": parsed_headers})

    # Step 5: Spot-check first 5 rows
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
                raise HTTPException(status_code=400, detail=f"Row {index+1}: {field} is not a valid SHA-256 hash")
            
    # Register + hand off
    register_batch(routing_metadata.account, routing_metadata.batch_id, request_id)
    checkpoint(request_id, Checkpoint.BATCH_REGISTERED, {"batch_id": routing_metadata.batch_id})
    total_rows = max(len(csv_str.splitlines()) - 1, 0)

    if routing_metadata.platform == "meta":
        background_tasks.add_task(process_meta_upload, request_id, csv_str, routing_metadata)
    elif routing_metadata.platform == "googleads":
        background_tasks.add_task(process_google_ads_upload, request_id, csv_str, routing_metadata)
    else:
        raise HTTPException(status_code=501, detail=f"Platform '{routing_metadata.platform}' not yet implemented")

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"request_id": request_id, "status": "processing", "rows_received": total_rows}
    )


@app.get("/status/{request_id}")
async def get_status(request_id: str, token: str = Depends(verify_token)):
    record = get_audit(request_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"No record found for request_id: {request_id}")
    return JSONResponse(status_code=200, content=record)