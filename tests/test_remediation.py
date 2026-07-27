from src.feedback.status_parser import parse_status_advice
from src.feedback.reconcile import reconcile
from src.feedback.remediation import determine_remediation_actions

with open("data/sample_status_advice.xml") as f:
    SAMPLE_XML = f.read()

PARSED = parse_status_advice(SAMPLE_XML)

SUBMITTED_REPORTS = {
    "00987654321009876543TXN13": {
        "transaction_reference_number": "00987654321009876543TXN13",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
    },
    "00987654321009876543TXN151": {
        "transaction_reference_number": "00987654321009876543TXN151",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
    },
    "TRD-001": {
        "transaction_reference_number": "TRD-001",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
    },
}


def test_rejected_transaction_gets_cancel_and_resubmit_action():
    reconciled = reconcile(list(SUBMITTED_REPORTS.keys()), PARSED)
    actions = determine_remediation_actions(reconciled, SUBMITTED_REPORTS)

    rejected_action = [a for a in actions if a["reference"] == "00987654321009876543TXN13"][0]
    assert rejected_action["action"] == "CANCEL_AND_RESUBMIT"
    assert rejected_action["cancellation"]["report_status"] == "CANC"
    assert rejected_action["rejection_reasons"][0]["code"] == "CON-412"


def test_pending_transaction_gets_wait_action():
    reconciled = reconcile(list(SUBMITTED_REPORTS.keys()), PARSED)
    actions = determine_remediation_actions(reconciled, SUBMITTED_REPORTS)

    pending_action = [a for a in actions if a["reference"] == "00987654321009876543TXN151"][0]
    assert pending_action["action"] == "WAIT"


def test_accepted_transaction_gets_no_action():
    reconciled = reconcile(list(SUBMITTED_REPORTS.keys()), PARSED)
    actions = determine_remediation_actions(reconciled, SUBMITTED_REPORTS)

    accepted_action = [a for a in actions if a["reference"] == "TRD-001"][0]
    assert accepted_action["action"] == "NONE"