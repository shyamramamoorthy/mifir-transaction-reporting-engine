from datetime import datetime

from src.lifecycle.report_status import (
    next_working_day_deadline,
    is_report_late,
    build_cancellation,
    correct_report,
)


def test_deadline_is_next_day_when_trade_is_midweek():
    trade_dt = datetime(2024, 3, 12, 10, 0, 0)  # Tuesday
    assert next_working_day_deadline(trade_dt) == datetime(2024, 3, 13, 23, 59, 59)


def test_deadline_skips_weekend_when_trade_is_friday():
    trade_dt = datetime(2024, 3, 15, 16, 0, 0)  # Friday
    assert next_working_day_deadline(trade_dt) == datetime(2024, 3, 18, 23, 59, 59)  # Monday


def test_is_report_late_true_when_submitted_after_deadline():
    trade_dt = datetime(2024, 3, 12, 10, 0, 0)
    submitted_dt = datetime(2024, 3, 14, 9, 0, 0)
    assert is_report_late(trade_dt, submitted_dt) is True


def test_is_report_late_false_when_submitted_same_day():
    trade_dt = datetime(2024, 3, 12, 10, 0, 0)
    submitted_dt = datetime(2024, 3, 12, 15, 0, 0)
    assert is_report_late(trade_dt, submitted_dt) is False


def test_build_cancellation_has_correct_status_and_reference():
    report = {
        "transaction_reference_number": "TRD-001",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
        "price": "189.5",
    }
    cancellation = build_cancellation(report)
    assert cancellation["report_status"] == "CANC"
    assert cancellation["transaction_reference_number"] == "TRD-001"
    assert "price" not in cancellation


def test_correct_report_returns_cancel_then_new_in_order():
    original = {
        "transaction_reference_number": "TRD-001",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
        "price": "189.5",
    }
    corrected = {**original, "price": "190.0", "report_status": "NEWT"}
    sequence = correct_report(original, corrected)
    assert sequence[0]["report_status"] == "CANC"
    assert sequence[1]["report_status"] == "NEWT"
    assert sequence[1]["price"] == "190.0"