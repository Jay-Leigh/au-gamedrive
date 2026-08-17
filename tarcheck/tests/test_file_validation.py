import pytest
from services.file_validation import validate_filename
from exceptions import FilenameValidationError

def test_valid_meta_filename():
    result = validate_filename("realbeds_QualifiedLead_meta_20260526_001_update.csv")
    assert result.account == "realbeds"
    assert result.audience_name == "QualifiedLead"
    assert result.platform == "meta"
    assert result.date == "20260526"
    assert result.batch_id == "001"
    assert result.action == "update"

def test_valid_google_filename():
    result = validate_filename("realbeds_QualifiedLead_googleads_20260526_001_update.csv")
    assert result.platform == "googleads"

def test_valid_replace_filename():
    result = validate_filename("realbeds_QualifiedLead_meta_20260526_001_replace.csv")
    assert result.action == "replace"

def test_wrong_part_count_raises():
    with pytest.raises(FilenameValidationError, match="exactly 6 parts"):
        validate_filename("too_few_parts.csv")

def test_unknown_account_raises():
    with pytest.raises(FilenameValidationError, match="Unknown account"):
        validate_filename("fakeclient_QualifiedLead_meta_20260526_001_update.csv")

def test_empty_eventname_raises():
    with pytest.raises(FilenameValidationError, match="cannot be empty"):
        validate_filename("realbeds__meta_20260526_001_update.csv")

def test_invalid_platform_raises():
    with pytest.raises(FilenameValidationError, match="Invalid platform"):
        validate_filename("realbeds_QualifiedLead_tiktok_20260526_001_update.csv")

def test_bad_date_format_raises():
    with pytest.raises(FilenameValidationError, match="YYYYMMDD"):
        validate_filename("realbeds_QualifiedLead_meta_2026-05-26_001_update.csv")

def test_non_numeric_batch_id_raises():
    with pytest.raises(FilenameValidationError, match="batchID must be numeric"):
        validate_filename("realbeds_QualifiedLead_meta_20260526_abc_update.csv")

def test_seven_parts_raises():
    with pytest.raises(FilenameValidationError, match="exactly 6 parts"):
        validate_filename("realbeds_QualifiedLead_extra_meta_20260526_001_update.csv")

def test_invalid_action_raises():
    with pytest.raises(FilenameValidationError, match="Input should be"):
        validate_filename("realbeds_QualifiedLead_meta_20260526_001_delete.csv")

def test_all_approved_accounts_pass():
    for account in ["realbeds"]:
        result = validate_filename(f"{account}_QualifiedLead_meta_20260526_001_update.csv")
        assert result.account == account
