def test_missing_token_returns_403(client):
    """No Authorization header → FastAPI returns 403 (HTTPBearer default)."""
    response = client.post("/upload")
    assert response.status_code == 401

def test_wrong_token_returns_401(client):
    response = client.post(
        "/upload",
        headers={"Authorization": "Bearer WRONG_TOKEN"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_correct_token_passes_auth(client, auth_header, valid_csv_bytes, valid_filename):
    """Correct token reaches the endpoint logic (not blocked by auth)."""
    response = client.post(
        "/upload",
        headers=auth_header,
        files={"file": (valid_filename, valid_csv_bytes, "text/csv")},
    )
    assert response.status_code != 401
    assert response.status_code != 403
