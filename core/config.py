# config.py
import re, os
from typing import Dict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    api_token: Optional[str] = os.getenv("SYSTEM_TOKEN")
    meta_access_token: str = ""
    database_url: str = "sqlite:///./test_audience_uploader.db"
    gcs_bucket_name: str = "audience-sync-bucket"
    app_env: str = "development"
    # Max file size handled by GCP infrastructure — not enforced here

    # Pre-approved accounts — will be replaced by PostgreSQL DB lookup in production
    # TODO: Replace this dict with a DB lookup via db/models.py → ApprovedAccount
    # when migrating to PostgreSQL on Cloud Run
    approved_accounts: Dict[str, Dict] = { # in future read from DB
        "realbeds": {
            "meta_audience_id": "120253772920450348",
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

    sha256_regex: re.Pattern = re.compile(r"^[a-f0-9]{64}$") # dont need to add
    supported_platforms: list[str] = ["meta", "googleads"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

