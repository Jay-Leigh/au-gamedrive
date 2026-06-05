from pydantic import BaseModel

class RoutingMetadata(BaseModel):
    filename: str
    account: str
    platform: str
    date: str
    audience_name: str
    batch_id: str

class Audience(BaseModel):
    pass
