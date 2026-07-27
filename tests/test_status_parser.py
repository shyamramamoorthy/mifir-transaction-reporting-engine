from src.feedback.status_parser import parse_status_advice

with open("data/sample_status_advice.xml") as f:
    SAMPLE_XML = f.read()


def test_parses_overall_report_status():
    result = parse_status_advice(SAMPLE_XML)
    assert result["report_status"] == "PART"


def test_parses_total_records():
    result = parse_status_advice(SAMPLE_XML)
    assert result["total_records"] == 8


def test_parses_records_per_status_counts():
    result = parse_status_advice(SAMPLE_XML)
    assert result["records_per_status"] == {"PDNG": 3, "RJCT": 2, "ACPT": 3}


def test_parses_rejected_transaction_with_error_detail():
    result = parse_status_advice(SAMPLE_XML)
    rejected = [t for t in result["transaction_feedback"] if t["reference"] == "00987654321009876543TXN13"][0]
    assert rejected["status"] == "RJCT"
    assert rejected["errors"][0]["code"] == "CON-412"


def test_parses_pending_transaction():
    result = parse_status_advice(SAMPLE_XML)
    pending = [t for t in result["transaction_feedback"] if t["reference"] == "00987654321009876543TXN151"][0]
    assert pending["status"] == "PDNG"


def test_five_transactions_have_explicit_feedback():
    result = parse_status_advice(SAMPLE_XML)
    assert len(result["transaction_feedback"]) == 5