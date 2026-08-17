from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from core.auth import verify_token
from services.audit_logging import get_audit

router = APIRouter()

@router.get("/status/{request_id}")
async def get_status(request_id: str, token: str = Depends(verify_token)):
    record = get_audit(request_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"No record found for request_id: {request_id}")
    return JSONResponse(status_code=200, content=record)
