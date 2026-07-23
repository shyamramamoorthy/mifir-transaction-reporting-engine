"""
Tests for the LEI checksum validator.

Reference LEIs are real, publicly-registered entities (see docs/sources.md).
"""

from src.identifiers.lei import is_valid_lei
from src.identifiers.isin import is_valid_isin


def test_accepts_real_barclays_lei():
    # Barclays Bank PLC — real GLEIF-registered LEI
    assert is_valid_lei("G5GSEF7VJP5I7OUK5573") is True


def test_accepts_real_deutsche_bank_lei():
    # Deutsche Bank Aktiengesellschaft — real GLEIF-registered LEI
    assert is_valid_lei("7LTWFZYICNSX8D621K86") is True


def test_rejects_typo_in_valid_lei():
    # Barclays' real LEI with the last character changed — must break the checksum
    assert is_valid_lei("G5GSEF7VJP5I7OUK5574") is False


def test_lei_rejects_wrong_length():
    assert is_valid_lei("TOOSHORT") is False


def test_is_case_and_whitespace_tolerant():
    # Our function .strip()s and .upper()s internally, so this should still pass
    assert is_valid_lei(" g5gsef7vjp5i7ouk5573 ") is True

def test_accepts_apple_isin():
    assert is_valid_isin("US0378331005") is True


def test_accepts_hsbc_isin():
    assert is_valid_isin("GB0002634946") is True


def test_accepts_deutsche_bank_isin():
    assert is_valid_isin("DE0005140008") is True


def test_rejects_corrupted_check_digit():
    assert is_valid_isin("US0378331006") is False


def test_isin_rejects_wrong_length():
    assert is_valid_isin("TOOSHORT") is False


def test_rejects_letter_as_check_digit():
    assert is_valid_isin("US037833100X") is False
