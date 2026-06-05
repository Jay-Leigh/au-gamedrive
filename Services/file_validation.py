# Services/file_validation_service.py
import re
from fastapi import HTTPException
from config import settings
from Models.base import RoutingMetadata

__all__ = ["validate_filename", "validate_sha256", "spot_check_rows"]

def validate_filename(filename: str) -> RoutingMetadata:
    clean_name = filename.replace(".csv", "")
    parts = clean_name.split("_")
 
    if len(parts) != 5:
        raise HTTPException(status_code=400, detail="Filename must have exactly 5 parts: account_eventname_platform_YYYYMMDD_batchID")
 
    account, eventname, platform, date_str, batchID = parts
 
    if account not in settings.approved_accounts:
        raise HTTPException(status_code=400, detail=f"Unknown account: {account}")
    if not eventname or not eventname.strip():
        raise HTTPException(status_code=400, detail="Audience name cannot be empty")
    if platform != "meta" and platform != "googleads":
        raise HTTPException(status_code=400, detail=f"Invalid platform. Got: {platform}")
    if not re.match(r"^[0-9]{8}$", date_str):
        raise HTTPException(status_code=400, detail=f"Date must be YYYYMMDD format. Got: {date_str}")
    if not batchID.isdigit():
        raise HTTPException(status_code=400, detail=f"batchID must be numeric. Got: {batchID}")
 
    return RoutingMetadata(
        filename=filename,
        account=account,
        audience_name=eventname,
        platform=platform,
        date=date_str,
        batch_id=batchID
    )