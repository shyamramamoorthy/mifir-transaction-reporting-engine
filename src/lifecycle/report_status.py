"""
Report lifecycle: T+1 deadline and the cancel-then-resubmit correction
workflow (there is no dedicated "correction" status under RTS 22).

Source: MiFIR Article 26(1) (T+1 deadline); ESMA/2016/1521 Technical
Reporting Instructions, section 6.2 (New vs Cancellation report structure).
"""

from datetime import datetime, timedelta


def next_working_day_deadline(trade_datetime: datetime) -> datetime:
    """
    Return the Article 26(1) reporting deadline for a trade: 23:59:59 on
    the next working day after execution.

    Simplification: only weekends are treated as non-working days. Public
    holidays are jurisdiction-specific (differ per NCA) and would need a
    maintained calendar in a real system -- not built here, flagged rather
    than silently ignored.
    """
    next_day = trade_datetime + timedelta(days=1)
    while next_day.weekday() >= 5:  # Monday=0 ... Saturday=5, Sunday=6
        next_day += timedelta(days=1)
    return next_day.replace(hour=23, minute=59, second=59, microsecond=0)


def is_report_late(trade_datetime: datetime, submission_datetime: datetime) -> bool:
    """True if submission_datetime falls after the Article 26(1) deadline."""
    return submission_datetime > next_working_day_deadline(trade_datetime)


def build_cancellation(report: dict) -> dict:
    """
    Build a CANC record for a previously-submitted report. Per ESMA's
    instructions, a cancellation only needs enough fields to identify the
    report being withdrawn, not the full trade detail again.
    """
    return {
        "report_status": "CANC",
        "transaction_reference_number": report["transaction_reference_number"],
        "executing_entity_id": report["executing_entity_id"],
        "submitting_entity_id": report["submitting_entity_id"],
    }


def correct_report(original_report: dict, corrected_report: dict) -> list:
    """
    Build the two-record sequence required to correct a submitted report:
    a CANC of the original, followed by a NEWT of the corrected version.
    Order matters -- the CANC must reach the ARM before the replacement.
    """
    cancellation = build_cancellation(original_report)
    corrected_report = dict(corrected_report)
    corrected_report["report_status"] = "NEWT"
    return [cancellation, corrected_report]