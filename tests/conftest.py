import pytest
from fastapi.testclient import TestClient
from main import app
from core.config import settings
from services.audit_logging import reset_audit_state

VALID_HASH = "a744863d83aefc35f62f9a247025dedfc8964b3c0b39dd794dd3816851fc4a94"
VALID_HASH_2 = "bb7ec47b853642a8aa2559c55103232581738375869de1926f83e12c4f26e6d4"

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_audit():
    reset_audit_state()

@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {settings.api_token}"}

@pytest.fixture
def valid_csv_bytes():
    content = (
        "em,ph,fn,ln,external_id,event_name,event_time\n"
        f"{VALID_HASH},{VALID_HASH_2},{VALID_HASH},{VALID_HASH},CRM-001,QualifiedLead,1746000000\n"
    )
    return content.encode("utf-8")

@pytest.fixture
def valid_filename():
    return "realbeds_QualifiedLeads_meta_20260526_002_update.csv"

@pytest.fixture
def valid_google_filename():
    return "realbeds_QualifiedLeads_googleads_20260526_002_update.csv"

@pytest.fixture
def valid_replace_filename():
    return "realbeds_QualifiedLeads_meta_20260526_002_replace.csv"

@pytest.fixture
def missing_header_csv_bytes():
    content = "em,ph,external_id\nfoo,bar,baz\n"
    return content.encode("utf-8")

@pytest.fixture
def invalid_hash_csv_bytes():
    content = (
        "em,ph,fn,ln,external_id,event_name,event_time\n"
        "not_a_hash,not_a_hash,x,x,CRM-001,QualifiedLead,1746000000\n"
    )
    return content.encode("utf-8")
