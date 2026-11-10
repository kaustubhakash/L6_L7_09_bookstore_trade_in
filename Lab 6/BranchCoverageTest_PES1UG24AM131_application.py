import pytest

from bookstore_trade_in import (
    process_book_buybacks,
    inspect_scanner_calibration,
)


@pytest.mark.parametrize("format_type", [
    "textbook", "hardcover", "paperback"
])
def test_supported_formats(format_type):
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": format_type,
            "books": [{"condition": "good"}],
        }],
        0,
    )
    assert result["status"] == "COMPLETED"


def test_unapproved_batch_is_skipped():
    result = process_book_buybacks(
        [{"intake_approved": False}], 0
    )
    assert result["status"] == "ZERO_CREDIT"


def test_unknown_format_is_rejected():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "magazine",
            "books": [],
        }],
        0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_missing_pages_branch():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"missing_pages": 1}],
        }],
        0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_branch():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"counterfeit": True}],
        }],
        0,
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_textbook_break_branch():
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


@pytest.mark.parametrize("condition", ["mint", "poor", "good"])
def test_condition_branches(condition):
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"condition": condition}],
        }],
        0,
    )
    assert result["status"] == "COMPLETED"


def test_credit_bonus_branch():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "payout_in_credit": True,
            "books": [{"condition": "good"}],
        }],
        5,
    )
    assert result["total_payout"] > 8.0


def test_audit_rejected_branch():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"missing_pages": 1} for _ in range(5)],
        }],
        0,
    )
    assert result["status"] == "AUDIT_REJECTED"


def test_zero_credit_branch():
    result = process_book_buybacks([], 0)
    assert result["status"] == "ZERO_CREDIT"


def test_completed_branch():
    result = process_book_buybacks(
        [{
            "intake_approved": True,
            "format": "paperback",
            "books": [{"condition": "good"}],
        }],
        0,
    )
    assert result["status"] == "COMPLETED"


def test_empty_scanner_branch():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_high_errors_consecutive():
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"


def test_scanner_low_error_resets_streak():
    assert inspect_scanner_calibration([[6, 2, 7]]) == "CALIBRATED"


def test_scanner_error_at_threshold():
    assert inspect_scanner_calibration([[5, 5, 5]]) == "CALIBRATED"


def test_scanner_multiple_devices():
    assert inspect_scanner_calibration([[6], [1, 2]]) == "CALIBRATED"


def test_invalid_input_branches():
    with pytest.raises(ValueError):
        process_book_buybacks(None, 0)

    with pytest.raises(ValueError):
        process_book_buybacks([], -1)
