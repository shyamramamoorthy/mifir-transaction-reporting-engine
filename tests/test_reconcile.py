from src.feedback.status_parser import parse_status_advice
from src.feedback.reconcile import reconcile

with open("data/sample_status_advice.xml") as f:
    SAMPLE_XML = f.read()

PARSED = parse_status_advice(SAMPLE_XML)


def test_rejected_reference_keeps_its_status_and_error():
    result = reconcile(["00987654321009876543TXN13"], PARSED)
    assert result["00987654321009876543TXN13"]["status"] == "RJCT"
    assert result["00987654321009876543TXN13"]["errors"][0]["code"] == "CON-412"


def test_pending_reference_keeps_its_status():
    result = reconcile(["00987654321009876543TXN151"], PARSED)
    assert result["00987654321009876543TXN151"]["status"] == "PDNG"


def test_reference_absent_from_feedback_defaults_to_accepted():
    # TRD-001 was never mentioned in this status advice message at all --
    # per ESMA paragraph 111, that means it was accepted.
    result = reconcile(["TRD-001"], PARSED)
    assert result["TRD-001"]["status"] == "ACPT"
    assert result["TRD-001"]["errors"] == []


def test_reconcile_handles_a_mixed_batch_in_one_call():
    result = reconcile(["00987654321009876543TXN13", "TRD-001"], PARSED)
    assert result["00987654321009876543TXN13"]["status"] == "RJCT"
    assert result["TRD-001"]["status"] == "ACPT"