from services.audit_logging import (
    checkpoint,
    Checkpoint,
    write_audit,
    get_audit,
    get_checkpoints,
    is_duplicate_batch,
    register_batch,
    reset_audit_state,
)

def test_checkpoint_creates_record():
    checkpoint("req-1", Checkpoint.FILE_RECEIVED, {"filename": "test.csv"})
    checkpoints = get_checkpoints("req-1")
    assert len(checkpoints) == 1
    assert checkpoints[0]["checkpoint"] == "file_received"

def test_multiple_checkpoints_append():
    checkpoint("req-1", Checkpoint.FILE_RECEIVED)
    checkpoint("req-1", Checkpoint.FILENAME_VALIDATED)
    checkpoint("req-1", Checkpoint.HEADERS_VALIDATED)
    checkpoints = get_checkpoints("req-1")
    assert len(checkpoints) == 3

def test_write_audit_stores_record():
    write_audit("req-1", {
        "filename": "test.csv", "account": "realbeds", "platform": "meta",
        "audience_name": "QualifiedLead", "total_rows": 10, "valid_rows": 10,
        "invalid_rows": None, "dispatched": 1, "succeeded": 1, "failed": None,
        "overall_status": "completed",
    })
    record = get_audit("req-1")
    assert record["overall_status"] == "completed"
    assert record["total_rows"] == 10

def test_get_audit_returns_none_for_unknown():
    assert get_audit("nonexistent") is None

def test_register_batch_marks_as_duplicate():
    assert not is_duplicate_batch("realbeds", "001")
    register_batch("realbeds", "001", "req-1")
    assert is_duplicate_batch("realbeds", "001")

def test_different_accounts_same_batch_not_duplicate():
    register_batch("realbeds", "001", "req-1")
    assert not is_duplicate_batch("africanoverlandtours", "001")

def test_reset_clears_all_state():
    register_batch("realbeds", "001", "req-1")
    write_audit("req-1", {
        "filename": "test.csv", "account": "realbeds", "platform": "meta",
        "audience_name": "QualifiedLead", "total_rows": 1, "valid_rows": 1,
        "invalid_rows": None, "dispatched": 1, "succeeded": 1, "failed": None,
        "overall_status": "completed",
    })
    reset_audit_state()
    assert get_audit("req-1") is None
    assert not is_duplicate_batch("realbeds", "001")
