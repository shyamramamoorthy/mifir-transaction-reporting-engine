"""
Take one trade from data/sample_trades.csv through the full pipeline:
map -> validate -> (if clean) export to XML.

Usage:
    python3 scripts/run_pipeline.py TRD-001
    python3 scripts/run_pipeline.py TRD-009
"""

import argparse
import csv

from src.mapping.field_mapper import map_trade_to_rts22
from src.validation.engine import ValidationEngine
from src.export.xml_writer import build_transaction_xml


def load_trade(trade_id: str) -> dict:
    with open("data/sample_trades.csv") as f:
        for row in csv.DictReader(f):
            if row["trade_id"] == trade_id:
                return row
    raise ValueError(f"No trade found with id {trade_id}")


def main():
    parser = argparse.ArgumentParser(description="Run one trade through the pipeline.")
    parser.add_argument("trade_id", help="e.g. TRD-001")
    args = parser.parse_args()

    raw_trade = load_trade(args.trade_id)
    print(f"Raw trade: {raw_trade}\n")

    report = map_trade_to_rts22(raw_trade)
    errors = ValidationEngine().validate(report)

    if errors:
        print(f"REJECTED — {len(errors)} error(s):")
        for error in errors:
            print(f"  [{error['rule']}] {error['field']}: {error['message']}")
        return

    print("PASSED validation. Generating XML:\n")
    print(build_transaction_xml(report))


if __name__ == "__main__":
    main()