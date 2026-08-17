# models/audience.py
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from core.config import settings


class AudienceMember(BaseModel):
    """Single CSV row — one audience member record."""
    em: Optional[str] = None
    ph: Optional[str] = None
    fn: Optional[str] = None
    ln: Optional[str] = None
    external_id: Optional[str] = None
    event_name: str
    event_time: str

    @field_validator("em", "ph", "fn", "ln")
    @classmethod
    def validate_hash(cls, v, info):
        if v is None or v == "":
            return None
        if not settings.sha256_regex.match(v):
            raise ValueError(f"{info.field_name}: invalid SHA-256 hash")
        return v

    @field_validator("em", "ph", mode="after")
    @classmethod
    def require_at_least_one_identifier(cls, v, info):
        return v

    def has_identifier(self) -> bool:
        return bool(self.em or self.ph)


class AudienceUploadSummary(BaseModel):
    """Response shape for upload status polling."""
    request_id: str
    filename: str
    account: str
    platform: str
    audience_name: str
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: list = Field(default_factory=list)
    dispatched: int = 0
    succeeded: int = 0
    failed: list = Field(default_factory=list)
    overall_status: str = "processing"