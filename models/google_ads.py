from pydantic import BaseModel
from typing import List, Optional

class Consent(BaseModel):
    # Valid values: "GRANTED" or "DENIED"
    ad_user_data: str = "GRANTED" 
    ad_personalization: str = "GRANTED"

class UserIdentifier(BaseModel):
    hashed_email: Optional[str] = None
    hashed_phone_number: Optional[str] = None
    hashed_first_name: Optional[str] = None
    hashed_last_name: Optional[str] = None

class UserData(BaseModel):
    user_identifiers: List[UserIdentifier]

class GoogleAdsBatchPayload(BaseModel):
    customer_id: str
    user_list_id: str
    operations: List[UserData]
    consent: Consent