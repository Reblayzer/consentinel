"""Unit tests for the heuristic PII classifier."""

from app.domain.enums import PIICategory
from app.pii.classifier import classify_field


def test_detects_email_by_values_and_name():
    result = classify_field("email", ["alice@example.com", "bob@lego.dk"])
    assert result.category == PIICategory.EMAIL
    assert result.is_personal_data
    assert result.confidence >= 0.9  # value + name signals agree


def test_detects_danish_cpr_as_national_id():
    result = classify_field("cpr_nummer", ["010203-1234", "151199-5678"])
    assert result.category == PIICategory.NATIONAL_ID
    assert result.confidence >= 0.9


def test_detects_name_by_column_name_only():
    # 'fornavn' is Danish for 'first name'; the values themselves look generic.
    result = classify_field("fornavn", ["Anders", "Mette", "Lars"])
    assert result.category == PIICategory.NAME


def test_ignores_non_pii_column():
    result = classify_field("order_total", ["12.50", "99.00", "3.20"])
    assert result.category == PIICategory.NONE
    assert not result.is_personal_data


def test_credit_card_requires_valid_luhn():
    valid = classify_field("payment_card", ["4111 1111 1111 1111"])
    assert valid.category == PIICategory.CREDIT_CARD

    invalid = classify_field("payment_card", ["1234 5678 9012 3456"])
    assert invalid.category != PIICategory.CREDIT_CARD


def test_partial_match_yields_low_confidence():
    # Only one of three values is an email → flagged, but not confidently.
    result = classify_field("contact", ["alice@example.com", "n/a", "unknown"])
    assert result.category == PIICategory.EMAIL
    assert result.confidence < 0.5
