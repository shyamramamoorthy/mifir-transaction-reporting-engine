import xml.etree.ElementTree as ET

from src.export.xml_writer import build_transaction_xml


SAMPLE_REPORT = {
    "report_status": "NEWT",
    "transaction_reference_number": "TRD-001",
    "executing_entity_id": "529900T8BM49AURSDO55",
    "investment_firm_covered_by_mifid": "true",
    "submitting_entity_id": "529900T8BM49AURSDO55",
    "buyer_id": "213800MBWEIJDM5CU638",
    "seller_id": "MLU0ZO3ML4LN2LL2TL39",
    "transmission_of_order_indicator": "false",
    "trading_date_time": "2024-03-15T09:31:00Z",
    "trading_capacity": "DEAL",
    "quantity": "5000",
    "price": "189.5",
    "price_currency": "GBP",
    "venue": "XLON",
    "instrument_id": "GB00B24CGK77",
}


def test_new_report_produces_well_formed_xml():
    xml_string = build_transaction_xml(SAMPLE_REPORT)
    root = ET.fromstring(xml_string)  # raises if not well-formed XML
    assert root.tag == "{urn:iso:std:iso:20022:tech:xsd:auth.016.001.01}Document"


def test_new_report_contains_key_fields():
    xml_string = build_transaction_xml(SAMPLE_REPORT)
    assert "<TxId>TRD-001</TxId>" in xml_string
    assert 'Ccy="GBP"' in xml_string
    assert "<TradVn>XLON</TradVn>" in xml_string


def test_cancellation_uses_cxl_not_new():
    cancellation_report = {
        "report_status": "CANC",
        "transaction_reference_number": "TRD-001",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
    }
    xml_string = build_transaction_xml(cancellation_report)
    assert "<Cxl>" in xml_string
    assert "<New>" not in xml_string


def test_cancellation_does_not_include_trade_detail():
    cancellation_report = {
        "report_status": "CANC",
        "transaction_reference_number": "TRD-001",
        "executing_entity_id": "529900T8BM49AURSDO55",
        "submitting_entity_id": "529900T8BM49AURSDO55",
    }
    xml_string = build_transaction_xml(cancellation_report)
    assert "<Pric>" not in xml_string
    assert "<TradVn>" not in xml_string