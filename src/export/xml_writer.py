"""
Build an ISO 20022 (auth.016.001.01) XML transaction report from a mapped
RTS 22 report dict.

Covers the fields populated so far (report identification, buyer/seller,
trading details, instrument ID), using ESMA's own tag names -- pulled
directly from ESMA/2016/1521 Technical Reporting Instructions, not
invented. Full coverage of all 65 fields is a future extension.

Source: ESMA/2016/1521 Technical Reporting Instructions, section 6.2.
"""

import xml.etree.ElementTree as ET

NAMESPACE = "urn:iso:std:iso:20022:tech:xsd:auth.016.001.01"


def build_transaction_xml(report: dict) -> str:
    """Build the XML for a single transaction report (NEWT or CANC)."""
    document = ET.Element("Document", xmlns=NAMESPACE)
    tx_report = ET.SubElement(document, "FinInstrmRptgTxRpt")
    tx = ET.SubElement(tx_report, "Tx")

    if report.get("report_status") == "CANC":
        _build_cancellation_xml(tx, report)
    else:
        _build_new_report_xml(tx, report)

    ET.indent(document)
    return ET.tostring(document, encoding="unicode")


def _build_cancellation_xml(tx: ET.Element, report: dict) -> None:
    # Per ESMA's instructions, a cancellation only needs enough fields to
    # identify the report being withdrawn -- not the full trade again.
    cxl = ET.SubElement(tx, "Cxl")
    ET.SubElement(cxl, "TxId").text = report["transaction_reference_number"]
    ET.SubElement(cxl, "ExctgPty").text = report["executing_entity_id"]
    ET.SubElement(cxl, "SubmitgPty").text = report["submitting_entity_id"]


def _build_new_report_xml(tx: ET.Element, report: dict) -> None:
    new = ET.SubElement(tx, "New")
    ET.SubElement(new, "TxId").text = report["transaction_reference_number"]
    ET.SubElement(new, "ExctgPty").text = report["executing_entity_id"]
    ET.SubElement(new, "InvstmtPtyInd").text = report["investment_firm_covered_by_mifid"]
    ET.SubElement(new, "SubmitgPty").text = report["submitting_entity_id"]

    buyer = ET.SubElement(new, "Buyr")
    buyer_account_owner = ET.SubElement(buyer, "AcctOwnr")
    buyer_id_element = ET.SubElement(buyer_account_owner, "Id")
    ET.SubElement(buyer_id_element, "LEI").text = report["buyer_id"]

    seller = ET.SubElement(new, "Sellr")
    seller_account_owner = ET.SubElement(seller, "AcctOwnr")
    seller_id_element = ET.SubElement(seller_account_owner, "Id")
    ET.SubElement(seller_id_element, "LEI").text = report["seller_id"]

    transmission = ET.SubElement(new, "OrdrTrnsmssn")
    ET.SubElement(transmission, "TrnsmssnInd").text = report["transmission_of_order_indicator"]

    trade_details = ET.SubElement(new, "Tx")
    ET.SubElement(trade_details, "TradDt").text = report["trading_date_time"]
    ET.SubElement(trade_details, "TradgCpcty").text = report["trading_capacity"]

    quantity_element = ET.SubElement(trade_details, "Qty")
    ET.SubElement(quantity_element, "Unit").text = report["quantity"]

    price_wrapper = ET.SubElement(trade_details, "Pric")
    price_inner = ET.SubElement(price_wrapper, "Pric")
    monetary_value = ET.SubElement(price_inner, "MntryVal")
    amount = ET.SubElement(monetary_value, "Amt", Ccy=report["price_currency"])
    amount.text = report["price"]

    ET.SubElement(trade_details, "TradVn").text = report["venue"]

    instrument = ET.SubElement(new, "FinInstrm")
    ET.SubElement(instrument, "Id").text = report["instrument_id"]


if __name__ == "__main__":
    # Quick manual sanity check -- prints a NEWT and a CANC example.
    sample_report = {
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
    print(build_transaction_xml(sample_report))