"""
End-to-end integration test: takes one raw trade all the way through the
pipeline built across Days 2, 4, and 5 -- field mapping, validation, and
XML export -- and checks the output at each stage.

The other test files are unit tests: each checks one function/class in
isolation, with hand-built input. This one checks that the pieces we built
on separate days actually fit together when wired up the way a real
pipeline would use them.
"""

import csv
import xml.etree.ElementTree as ET

from src.mapping.field_mapper import map_trade_to_rts22
from src.validation.engine import ValidationEngine
from src.export.xml_writer import build_transaction_xml


def load_trade(trade_id: str) -> dict:
    with open("data/sample_trades.csv") as f:
        for row in csv.DictReader(f):
            if row["trade_id"] == trade_id:
                return row
    raise ValueError(f"No trade found with id {trade_id}")


def test_clean_trade_passes_through_the_whole_pipeline():
    raw_trade = load_trade("TRD-001")

    report = map_trade_to_rts22(raw_trade)
    errors = ValidationEngine().validate(report)
    assert errors == []

    xml_string = build_transaction_xml(report)
    root = ET.fromstring(xml_string)
    assert root.tag == "{urn:iso:std:iso:20022:tech:xsd:auth.016.001.01}Document"
    assert "<TxId>TRD-001</TxId>" in xml_string
    assert f"Ccy=\"{report['price_currency']}\"" in xml_string


def test_broken_trade_is_caught_before_it_ever_reaches_xml_export():
    raw_trade = load_trade("TRD-009")  # blank ISIN, placeholder LEIs

    report = map_trade_to_rts22(raw_trade)
    errors = ValidationEngine().validate(report)

    assert len(errors) > 0
    # The point of building validation before export: a broken report
    # never gets this far in a real pipeline. We only build the XML if
    # there were no errors.
    error_fields = {error["field"] for error in errors}
    assert "instrument_id" in error_fields