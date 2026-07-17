from typing import Literal
import re
from datetime import datetime
from pydantic import BaseModel, model_validator, field_validator
from core.config import settings

class RoutingMetadata(BaseModel):
    filename: str
    account: str
    audience_name: str
    platform: str
    date: str
    batch_id: str
    # action: str
    action: Literal["update", "replace"]

    @model_validator(mode="before")
    @classmethod
    def parse_filename(cls, data):
        raw = data["filename"]
        clean = raw.removesuffix(".csv")
        parts = clean.split("_")
        if len(parts) != 6:
            raise ValueError("Filename must have exactly 6 parts: account_audiencename_platform_YYYYMMDD_batchID_action")
        account, audience_name, platform, date_str, batch_id, action = parts
        data.update(account=account.lower(), audience_name=audience_name, platform=platform.lower(), date=date_str, batch_id=batch_id, action=action)
        return data

    @field_validator("account")
    @classmethod
    def check_account(cls, v):
        if v not in settings.approved_accounts:
            raise ValueError(f"Unknown account: {v}")
        return v

    @field_validator("audience_name")
    @classmethod
    def check_audience_name(cls, v):
        if not v.strip():
            raise ValueError("Audience name cannot be empty")
        return v

    @field_validator("platform")
    @classmethod
    def check_platform(cls, v):
        if v not in settings.supported_platforms:
            raise ValueError(f"Invalid platform. Got: {v}")
        return v

    @field_validator("date")
    @classmethod
    def check_date(cls, v):
        if not re.match(r"^[0-9]{8}$", v):
            raise ValueError(f"Date must be YYYYMMDD format. Got: {v}")
        try:
            datetime.strptime(v, "%Y%m%d")
        except ValueError:
            raise ValueError(f"Date is not a valid calendar date: {v}")
        return v

    @field_validator("batch_id")
    @classmethod
    def check_batch_id(cls, v):
        if not v.isdigit():
            raise ValueError(f"batchID must be numeric. Got: {v}")
        return v