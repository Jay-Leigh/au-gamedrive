# config.py
import re
from typing import Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    system_token: str = "DEFAULT_DEV_TOKEN"  # Obtain System Token
    meta_access_token: str = ""  # get Uploader Token
    # Max file size handled by GCP infrastructure — not enforced here

    # Pre-approved accounts — will be replaced by PostgreSQL DB lookup in production
    # TODO: Replace this dict with a DB lookup via db/models.py → ApprovedAccount
    # when migrating to PostgreSQL on Cloud Run
    approved_accounts: Dict[str, Dict] = {
        "realbeds": {
            "meta_audience_id": "YOUR_META_AUDIENCE_ID",
            "google_customer_id": "123-456-7890",
            "google_user_list_id": "987654321"
        },
        "realbeds1": {
            "meta_audience_id": "YOUR_META_AUDIENCE_ID",
            "google_customer_id": "123-456-7890",
            "google_user_list_id": "987654321"
        },
        "africanoverlandtours": {
            "meta_audience_id": "YOUR_META_AUDIENCE_ID_2",
            "google_customer_id": "111-222-3333",
            "google_user_list_id": "444555666"
        }
    }

    # approved_events removed — second filename part is now a free-form
    # custom audience label (e.g. "WarmLeads", "PurchasedQ1")
    # Filename convention: accountname_CustomAudienceName_platform_YYYYMMDD_batchID.csv

    sha256_regex: re.Pattern = re.compile(r"^[a-f0-9]{64}$")

    class Config:
        env_file = ".env"


settings = Settings()