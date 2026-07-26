"""
Command-line tool to check whether a sample trade is in scope for MiFIR
transaction reporting under a given regime.

Usage:
    python3 -m src.regime.cli SCOPE-001 --regime eu
    python3 -m src.regime.cli SCOPE-003 --regime uk_proposed
"""

import argparse
import csv

from src.regime.scope_rules import (
    is_in_scope_eu,
    is_in_scope_uk_current,
    is_in_scope_uk_proposed,
)

REGIME_FUNCTIONS = {
    "eu": is_in_scope_eu,
    "uk_current": is_in_scope_uk_current,
    "uk_proposed": is_in_scope_uk_proposed,
}


def load_trade(trade_id: str) -> dict:
    with open("data/regime_scope_examples.csv") as f:
        for row in csv.DictReader(f):
            if row["trade_id"] == trade_id:
                return row
    raise ValueError(f"No trade found with id {trade_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Check MiFIR reporting scope for a sample trade."
    )
    parser.add_argument("trade_id", help="e.g. SCOPE-001")
    parser.add_argument("--regime", choices=REGIME_FUNCTIONS.keys(), required=True)
    args = parser.parse_args()

    trade = load_trade(args.trade_id)
    check_function = REGIME_FUNCTIONS[args.regime]
    in_scope = check_function(trade)

    print(f"{trade['description']}")
    print(f"{args.trade_id} under {args.regime}: {'IN SCOPE' if in_scope else 'OUT OF SCOPE'}")


if __name__ == "__main__":
    main()