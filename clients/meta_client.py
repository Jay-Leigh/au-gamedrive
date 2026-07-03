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
            try:
                response = await client.post(url, params={"access_token": access_token}, json=payload_dict)
                response.raise_for_status()
                result = response.json()
                dispatch_results.append({
                    "batch_seq": batch.session.batch_seq,
                    "num_received": result.get("num_received", 0),
                    "num_invalid_entries": result.get("num_invalid_entries", 0),
                    "invalid_entry_samples": result.get("invalid_entry_samples", []),
                    "error": None
                })
            except httpx.HTTPStatusError as e:
                logging.error(f"[{request_id}] Meta dispatch failed batch {batch.session.batch_seq}: {e.response.text}")
                dispatch_results.append({
                    "batch_seq": batch.session.batch_seq,
                    "num_received": 0,
                    "num_invalid_entries": 0,
                    "invalid_entry_samples": [],
                    "error": e.response.text
                })
                
    return dispatch_results