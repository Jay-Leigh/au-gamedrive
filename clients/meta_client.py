import httpx
import logging
from typing import List, Dict, Any
from models.meta_ads import MetaBatchPayload

async def dispatch_batches_to_meta(
    payloads: List[MetaBatchPayload], 
    access_token: str, 
    request_id: str
) -> List[Dict[str, Any]]:
    
    dispatch_results = []
    
    async with httpx.AsyncClient() as client:
        for batch in payloads:
            url = f"https://graph.facebook.com/v25.0/{batch.audience_id}/users"
            
            payload_dict = {
                "session": batch.session.model_dump(),
                "payload": batch.payload.model_dump(by_alias=True)
            }
            dispatch_results.append({
                "batch_seq": batch.session.batch_seq,
                "num_received": len(batch.payload.data),
                "num_invalid_entries": 0,
                "invalid_entry_samples": [],
                "error": None
            })
                
    return dispatch_results