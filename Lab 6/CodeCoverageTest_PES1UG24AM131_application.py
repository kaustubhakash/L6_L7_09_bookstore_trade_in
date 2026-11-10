import pytest

from bookstore_trade_in import (
    process_book_buybacks,
    inspect_scanner_calibration,
)


def test_invalid_batches():
    with pytest.raises(ValueError):
        process_book_buybacks(None, 5)


def test_negative_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks([], -1)


def test_unapproved_batch():
    result = process_book_buybacks(
        [{"intake_approved": False}], 5
    )
    assert result["status"] == "ZERO_CREDIT"


def test_all_book_formats():
    batches = [
        {
            "intake_approved": True,
            "format": "textbook",
            "books": [{"missing_pages": 0, "condition": "good"}],
        },
        {
            "intake_approved": True,
            "format": "hardcover",
            "books": [{"missing_pages": 0, "condition": "good"}],
        },
        {
            "intake_approved": True,
            "format": "paperback",
            "books": [{"missing_pages": 0, "condition": "good"}],
        },
    ]
    result = process_book_buybacks(batches, 0)
    assert result["total_payout"] == 63.0
    assert result["status"] == "COMPLETED"


def test_unsupported_format():
    result = process_book_buybacks(
        [{"intake_approved": True, "format": "magazine"}], 5
    )
    assert result["status"] == "ZERO_CREDIT"


def test_missing_pages_rejected():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"missing_pages": 2}],
        }],
        0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_book():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"counterfeit": True}],
        }],
        0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_textbook_stops_batch():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "textbook",
            "books": [
                {"counterfeit": True},
                {"condition": "mint"},
            ],
        }],
        0,
    )
    assert result["total_payout"] == 0.0


def test_book_conditions():
    batches = [
        {
            "intake_approved": True,
            "format": "paperback",
            "books": [
                {"condition": "mint"},
                {"condition": "poor"},
                {"condition": "good"},
            ],
        }
    ]
    result = process_book_buybacks(batches, 0)
    assert result["total_payout"] == 21.2


def test_store_credit_bonus():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "payout_in_credit": True,
            "books": [{"condition": "good"}],
        }],
        5,
    )
    assert result["total_payout"] == 13.0


def test_audit_rejection():
    batches = [
        {
            "intake_approved": True,
            "format": "paperback",
            "books": [
                {"missing_pages": 1},
                {"missing_pages": 1},
                {"missing_pages": 1},
                {"missing_pages": 1},
                {"missing_pages": 1},
            ],
        }
    ]
    result = process_book_buybacks(batches, 0)
    assert result["status"] == "AUDIT_REJECTED"


def test_empty_scanner_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_calibrated():
    assert inspect_scanner_calibration([[1, 3, 5]]) == "CALIBRATED"


def test_scanner_recalibration():
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"
