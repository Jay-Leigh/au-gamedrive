class ValidationError(Exception):
    """Base for all validation failures in the pipeline."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class FilenameValidationError(ValidationError):
    """Filename does not match the required convention."""
    pass

class SchemaValidationError(ValidationError):
    """CSV headers or row data fails schema checks."""
    pass

class HashValidationError(ValidationError):
    """A field that should be SHA-256 hashed is not."""
    pass

class DuplicateBatchError(ValidationError):
    """batchID has already been processed for this account."""
    def __init__(self, detail: str):
        super().__init__(detail, status_code=409)

class EmptyFileError(ValidationError):
    """Uploaded file has zero bytes."""
    pass

class PlatformNotImplementedError(ValidationError):
    """Routing hit a platform with no handler."""
    def __init__(self, detail: str):
        super().__init__(detail, status_code=501)

class ActionNotImplementedError(ValidationError):
    """Replace action requested but REMOVE flow not built yet."""
    def __init__(self, detail: str):
        super().__init__(detail, status_code=501)