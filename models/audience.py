from pydantic import BaseModel, Field

class Audience(BaseModel):
    audience_name: str = Field(..., min_length=1)
