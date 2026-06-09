# Services/google_ads_processing_service.py
import csv
import io
import logging
from config import settings
from datetime import datetime
from Models.base import RoutingMetadata
from Models.google_ads import GoogleAdsBatchPayload, UserData, UserIdentifier, Consent
from Clients.google_ads_client import dispatch_batches_to_google_ads
from Services.audit_logging import write_audit, checkpoint, Checkpoint
from Services.storage import save_processed_csv, save_payload_json

async def process_google_ads_upload(request_id: str, csv_content: str, routing_metadata: RoutingMetadata):
    logging.info(f"[{request_id}] Starting Google Ads async processing...")
 
    reader = csv.DictReader(io.StringIO(csv_content))
    
    valid_operations = []
    invalid_rows = []
    
    # In a real scenario, you'd fetch this from your config/DB based on the account
    # For now, we mock the Customer ID and User List ID
    account_cfg = settings.approved_accounts[routing_metadata.account]
    customer_id = account_cfg["google_customer_id"]
    user_list_id = account_cfg["google_user_list_id"]

    # Step 1: Validate and Transform Rows
    for index, row in enumerate(reader):
        # We assume the spot check in main.py already validated hashes.
        # We map the CSV fields to Google's UserIdentifier schema
        em = row.get("em")
        ph = row.get("ph")

        if not em and not ph:
            invalid_rows.append({"row_index": index, "reason": "No identifiers present (em or ph required)"})
            continue

        identifier = UserIdentifier(
            hashed_email=em or None,
            hashed_phone_number=ph or None,
            hashed_first_name=row.get("fn") or None,
            hashed_last_name=row.get("ln") or None,
        )
        user_data = UserData(user_identifiers=[identifier])
        valid_operations.append(user_data)

    if not valid_operations:
        checkpoint(request_id, Checkpoint.ROWS_VALIDATED, {"valid": 0, "invalid": len(invalid_rows)})
        logging.error(f"[{request_id}] No valid operations for Google Ads. Aborting.")
        return
    
    checkpoint(request_id, Checkpoint.ROWS_VALIDATED, {"valid": len(valid_operations), "invalid": len(invalid_rows)})

    # Step 2: Build the Google Ads Payload
    # Google now requires consent flags, especially for EEA traffic
    payload = GoogleAdsBatchPayload(
        customer_id=customer_id,
        user_list_id=user_list_id,
        operations=valid_operations,
        consent=Consent(ad_user_data="GRANTED", ad_personalization="GRANTED")
    )

    checkpoint(request_id, Checkpoint.GOOGLE_PAYLOAD_CREATED, {"operations": len(valid_operations)})
    save_payload_json(request_id, "google", payload.model_dump())

    checkpoint(request_id, Checkpoint.GOOGLE_DISPATCH_STARTED)
    dispatch_result = await dispatch_batches_to_google_ads(payload, request_id)
    checkpoint(request_id, Checkpoint.GOOGLE_DISPATCH_COMPLETED)
    
    # Step 4: Write Audit Log (Similar to Meta, simplified here)
    record = {
        "request_id": request_id,
        "filename": routing_metadata.filename,
        "account": routing_metadata.account,
        "platform": "googleads",
        "eventname": routing_metadata.audience_name,
        "timestamp": datetime.now().isoformat(),
        "total_rows": len(valid_operations) + len(invalid_rows),
        "valid_rows": len(valid_operations),
        "invalid_rows": invalid_rows,
        "dispatched": len(valid_operations),
        "succeeded": dispatch_result.get("operations_processed", 0),
        "failed": [],
        "overall_status": "completed" if not dispatch_result.get("error") else "failed"
    }
    write_audit(request_id, record)
    logging.info(f"AUDIT LOG [{request_id}]: status={record['overall_status']}")