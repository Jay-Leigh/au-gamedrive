from exceptions import (
    ValidationError,
    FilenameValidationError,
    SchemaValidationError,
    HashValidationError,
    EmptyFileError,
    DuplicateBatchError,
    PlatformNotImplementedError,
    ActionNotImplementedError,
)

def test_filename_validation_error_is_400():
    exc = FilenameValidationError("bad filename")
    assert exc.status_code == 400
    assert exc.detail == "bad filename"

def test_schema_validation_error_is_400():
    exc = SchemaValidationError("missing column")
    assert exc.status_code == 400

def test_hash_validation_error_is_400():
    exc = HashValidationError("bad hash")
    assert exc.status_code == 400

def test_empty_file_error_is_400():
    exc = EmptyFileError("empty")
    assert exc.status_code == 400

def test_duplicate_batch_error_is_409():
    exc = DuplicateBatchError("already processed")
    assert exc.status_code == 409

def test_platform_not_implemented_is_501():
    exc = PlatformNotImplementedError("unknown platform")
    assert exc.status_code == 501

def test_action_not_implemented_is_501():
    exc = ActionNotImplementedError("replace not supported")
    assert exc.status_code == 501

def test_all_inherit_from_validation_error():
    for cls in [
        FilenameValidationError,
        SchemaValidationError,
        HashValidationError,
        EmptyFileError,
        DuplicateBatchError,
        PlatformNotImplementedError,
        ActionNotImplementedError,
    ]:
        assert issubclass(cls, ValidationError)

def test_exception_message_in_str():
    exc = FilenameValidationError("test detail")
    assert str(exc) == "test detail"
