from pydantic import BaseModel, Field

class Audience(BaseModel):
    audience_name: str = Field(..., min_length=1)

class AudienceFileName(BaseModel):
    filename: str
    account: str
    audience_name: str
    platform: str
    date: str
    batch_id: str