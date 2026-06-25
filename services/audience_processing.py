# Services/audience_processing_service.py
import csv, io, time, json, logging
from datetime import datetime
from core.config import settings
from models.base import RoutingMetadata
from models.meta_ads import MetaBatchPayload, MetaSession, MetaPayloadData
from clients.meta_client import dispatch_batches_to_meta
from services.audit_logging import write_audit, checkpoint, Checkpoint
from services.storage import save_processed_csv, save_payload_json

def write_audit_log(request_id, routing_metadata, total_rows, valid_rows_count, invalid_rows, dispatch_results, overall_status):
    failed_batches = [{"batch_seq": r["batch_seq"], "error": r["error"]} for r in dispatch_results if r.get("error")]
    succeeded_count = sum(r.get("num_received", 0) for r in dispatch_results if not r.get("error"))
 
    record = {
        "request_id": request_id,
        "filename": routing_metadata.filename,
        "account": routing_metadata.account,
        "platform": "meta",
        "eventname": routing_metadata.audience_name,
        "timestamp": datetime.now().isoformat(),
        "total_rows": total_rows,
        "valid_rows": valid_rows_count,
        "invalid_rows": invalid_rows,
        "dispatched": len(dispatch_results),
        "succeeded": succeeded_count,
        "failed": failed_batches,
        "overall_status": overall_status
    }
    write_audit(request_id, record)
    logging.info(f"AUDIT LOG [{request_id}]: status={overall_status} valid={valid_rows_count} succeeded={succeeded_count}")

async def process_meta_upload(request_id: str, csv_content: str, routing_metadata: RoutingMetadata):
    logging.info(f"[{request_id}] Starting async processing...")
 
    reader = csv.DictReader(io.StringIO(csv_content))
    headers = reader.fieldnames or []
 
    valid_rows = []
    invalid_rows = []
    hashed_fields = ["em", "ph"]
    required_strings = ["external_id", "event_name", "event_time"]
 
    # Step 4: Validate Rows
    checkpoint(request_id, Checkpoint.ROWS_VALIDATED)
    for index, row in enumerate(reader):
        row_valid = True
 
        for field in hashed_fields:
            val = row.get(field, "")
            if val and not settings.sha256_regex.match(val):
                invalid_rows.append({"row_index": index, "field": field, "reason": "Invalid SHA-256 hash"})
                row_valid = False
                break
 
        if row_valid:
            for field in required_strings:
                if not row.get(field):
                    invalid_rows.append({"row_index": index, "field": field, "reason": "Required field is empty"})
                    row_valid = False
                    break
 
        if row_valid:
            valid_rows.append(row)
 
    if not valid_rows:
        logging.error(f"[{request_id}] No valid rows after full validation. Aborting.")
        checkpoint(request_id, Checkpoint.ROWS_VALIDATED)
        write_audit_log(request_id, routing_metadata, len(invalid_rows), 0, invalid_rows, [], "failed")
        return
    
    checkpoint(request_id, Checkpoint.ROWS_VALIDATED, {"valid": len(valid_rows), "invalid": len(invalid_rows)})
    save_processed_csv(request_id, "meta", valid_rows)

    # Step 5: Transform to Meta Payload
    account_cfg = settings.approved_accounts[routing_metadata.account]
    audience_id = account_cfg["meta_audience_id"]
    schema = ["EMAIL", "PHONE", "EXTERN_ID"]
 
    if "fn" in headers: schema.append("FN")
    if "ln" in headers: schema.append("LN")
 
    data = []
    for row in valid_rows:
        record = []
        for meta_key in schema:
            if meta_key == "EMAIL": record.append(row.get("em"))
            elif meta_key == "PHONE": record.append(row.get("ph"))
            elif meta_key == "EXTERN_ID": record.append(row.get("external_id"))
            elif meta_key == "FN": record.append(row.get("fn"))
            elif meta_key == "LN": record.append(row.get("ln"))
        data.append(record)

    # Step 6: Batch Rows (10k limit)
    BATCH_SIZE = 10000
    batches = [data[i:i + BATCH_SIZE] for i in range(0, len(data), BATCH_SIZE)]
    session_id = int(time.time())
 
    payloads = []
    for index, batch in enumerate(batches):
        is_last = (index == len(batches) - 1)
        payloads.append(MetaBatchPayload(
                audience_id=audience_id,
                session=MetaSession(
                    session_id=session_id,
                    batch_seq=index + 1,
                    last_batch_flag=is_last,
                    estimated_num_total=len(data)
                ),
                payload=MetaPayloadData(**{"schema": schema, "data": batch})
        ))
    
    checkpoint(request_id, Checkpoint.PAYLOAD_CREATED, {"platform": "meta", "batches": len(payloads)})
    save_payload_json(request_id, "meta", [p.model_dump() for p in payloads])

    # Step 7: Dispatch to Meta
    checkpoint(request_id, Checkpoint.DISPATCH_STARTED, {"platform": "meta"})
    dispatch_results = await dispatch_batches_to_meta(payloads, settings.meta_access_token, request_id)
    checkpoint(request_id, Checkpoint.DISPATCH_COMPLETED, {"platform": "meta"})
    
    # Determine overall status
    failed_count = sum(1 for r in dispatch_results if r.get("error"))
    overall_status = "completed"
    if failed_count > 0:
        overall_status = "partial_failure" if failed_count < len(dispatch_results) else "failed"

    # Step 8: Write Audit Log
    total_rows = len(valid_rows) + len(invalid_rows)
    write_audit_log(request_id, routing_metadata, total_rows, len(valid_rows), invalid_rows, dispatch_results, overall_status)

