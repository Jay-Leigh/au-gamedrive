from exceptions import FilenameValidationError
from pydantic import ValidationError
from models.base import RoutingMetadata

def validate_filename(filename: str) -> RoutingMetadata:
    try:
        return RoutingMetadata(filename=filename)
    except ValidationError as e:
        raise FilenameValidationError(e.errors()[0]["msg"])