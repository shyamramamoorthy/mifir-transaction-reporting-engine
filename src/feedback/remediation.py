"""
Turns reconciliation results into next actions.

MiFIR's own correction workflow (Day 5) is CANC then NEWT -- but only a
human (or an upstream system) that understands *why* a transaction was
rejected can supply the corrected values. This module automates the part
that's genuinely mechanical (building the CANC record, which only needs
identifiers we already have) and stops there -- it does not attempt to
guess what the corrected data should be.

Source: builds on ESMA/2016/1521 section 6.3 (status codes) and the
CANC/NEWT correction workflow already sourced for Day 5.
"""

from src.lifecycle.report_status import build_cancellation


def determine_remediation_actions(reconciled: dict, submitted_reports: dict) -> list:
    """
    reconciled: output of reconcile.reconcile() -- {reference: {status, errors}}
    submitted_reports: {reference: original_report_dict} -- the full RTS22
        report originally submitted, needed to build a cancellation.
    """
    actions = []
    for reference, feedback in reconciled.items():
        if feedback["status"] == "RJCT":
            original_report = submitted_reports[reference]
            cancellation = build_cancellation(original_report)
            actions.append({
                "reference": reference,
                "action": "CANCEL_AND_RESUBMIT",
                "cancellation": cancellation,
                "rejection_reasons": feedback["errors"],
                "note": (
                    "Cancellation generated automatically. A corrected NEWT "
                    "report must be built from a fix to the underlying data "
                    "issue described above -- this tool cannot infer the "
                    "correct value."
                ),
            })
        elif feedback["status"] == "PDNG":
            actions.append({
                "reference": reference,
                "action": "WAIT",
                "note": "Still pending instrument reference data; no action needed yet.",
            })
        else:  # ACPT
            actions.append({
                "reference": reference,
                "action": "NONE",
                "note": "Accepted, nothing to do.",
            })
    return actions