from services.audit_logging import (
    checkpoint,
    Checkpoint,
    write_audit,
    get_audit,
    is_duplicate_batch,
    register_batch,
    reset_audit_state,
)

def test_checkpoint_creates_record():
    checkpoint("req-1", Checkpoint.FILE_RECEIVED, {"filename": "test.csv"})
    record = get_audit("req-1")
    assert record is not None
    assert len(record["checkpoints"]) == 1
    assert record["checkpoints"][0]["stage"] == "file_received"

def test_multiple_checkpoints_append():
    checkpoint("req-1", Checkpoint.FILE_RECEIVED)
    checkpoint("req-1", Checkpoint.FILENAME_VALIDATED)
    checkpoint("req-1", Checkpoint.HEADERS_VALIDATED)
    record = get_audit("req-1")
    assert len(record["checkpoints"]) == 3

def test_write_audit_stores_record():
    write_audit("req-1", {"status": "completed", "rows": 10})
    record = get_audit("req-1")
    assert record["status"] == "completed"
    assert record["rows"] == 10

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
    write_audit("req-1", {"status": "completed"})
    reset_audit_state()
    assert get_audit("req-1") is None
    assert not is_duplicate_batch("realbeds", "001")
