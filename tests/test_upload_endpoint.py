import os
import pytest

REAL_META_CSV = "test_csvs/realbeds_QualifiedLeads_meta_20260526_001_update.csv"
REAL_GOOGLE_CSV = "test_csvs/realbeds_QualifiedLeads_googleads_20260526_001_update.csv"

# --- In-memory unit-style E2E tests ---

def test_valid_meta_upload_returns_202(client, auth_header, valid_csv_bytes, valid_filename):
    response = client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_filename, valid_csv_bytes, "text/csv")},
    )
    assert response.status_code == 202
    body = response.json()
    assert "request_id" in body
    assert body["status"] == "processing"
    assert body["rows_received"] == 1

def test_valid_google_upload_returns_202(client, auth_header, valid_csv_bytes, valid_google_filename):
    response = client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_google_filename, valid_csv_bytes, "text/csv")},
    )
    assert response.status_code == 202

def test_status_returns_completed_after_upload(client, auth_header, valid_csv_bytes, valid_filename):
    upload = client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_filename, valid_csv_bytes, "text/csv")},
    )
    request_id = upload.json()["request_id"]
    status = client.get(f"/status/{request_id}", headers=auth_header)
    assert status.status_code == 200
    assert status.json()["overall_status"] == "completed"

def test_empty_file_returns_400(client, auth_header):
    response = client.post(
        "/upload",
        headers=auth_header,
       files={"file": ("realbeds_Lead_meta_20260526_003_update.csv", b"", "text/csv")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_missing_header_returns_400(client, auth_header, missing_header_csv_bytes):
    response = client.post(
        "/upload",
        headers=auth_header,
       files={"file": ("realbeds_Lead_meta_20260526_004_update.csv", missing_header_csv_bytes, "text/csv")},
    )
    assert response.status_code == 400
    assert "Missing required column" in response.json()["detail"]

def test_bad_hash_returns_400(client, auth_header, invalid_hash_csv_bytes):
    response = client.post(
        "/upload",
        headers=auth_header,
       files={"file": ("realbeds_Lead_meta_20260526_005_update.csv", invalid_hash_csv_bytes, "text/csv")},
    )
    assert response.status_code == 400
    assert "SHA-256" in response.json()["detail"]

def test_replace_action_returns_501(client, auth_header, valid_csv_bytes, valid_replace_filename):
    response = client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_replace_filename, valid_csv_bytes, "text/csv")},
    )
    assert response.status_code == 501
    assert "Replace" in response.json()["detail"]

def test_bad_filename_returns_400(client, auth_header, valid_csv_bytes):
    response = client.post(
        "/upload",
        headers=auth_header,
        files={"file": ("bad_filename.csv", valid_csv_bytes, "text/csv")},
    )
    assert response.status_code == 400

def test_duplicate_batch_returns_409(client, auth_header, valid_csv_bytes, valid_filename):
    client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_filename, valid_csv_bytes, "text/csv")},
    )
    response = client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_filename, valid_csv_bytes, "text/csv")},
    )
    assert response.status_code == 409
    assert "Duplicate" in response.json()["detail"]

def test_unknown_request_id_returns_404(client, auth_header):
    response = client.get("/status/nonexistent-id", headers=auth_header)
    assert response.status_code == 404

# --- Integration tests with real test_csvs files ---

@pytest.mark.skipif(not os.path.exists(REAL_META_CSV), reason="Real meta CSV not found")
def test_real_meta_csv_upload(client, auth_header):
    with open(REAL_META_CSV, "rb") as f:
        filename = os.path.basename(REAL_META_CSV)
        response = client.post(
            "/upload",
            headers=auth_header,
            files={"file": (filename, f.read(), "text/csv")},
        )

        print("\nSTATUS:", response.status_code)
        print("BODY:", response.text)
    assert response.status_code == 202

@pytest.mark.skipif(not os.path.exists(REAL_GOOGLE_CSV), reason="Real Google CSV not found")
def test_real_google_csv_upload(client, auth_header):
    with open(REAL_GOOGLE_CSV, "rb") as f:
        filename = os.path.basename(REAL_GOOGLE_CSV)
        response = client.post(
            "/upload",
            headers=auth_header,
            files={"file": (filename, f.read(), "text/csv")},
        )
    assert response.status_code == 202
