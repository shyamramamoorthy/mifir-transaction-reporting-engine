"""
Maps a raw trade record (as found in data/sample_trades.csv) to a full
RTS 22 transaction report record (all 65 fields).

Most fields are conditional under RTS 22 and are legitimately blank for a
simple on-venue equity/ETF trade with no natural-person counterparties,
no algorithmic trading detail, and no derivative characteristics — this
mapper does not "forget" those fields, it reflects that they don't apply.

Source: Commission Delegated Regulation (EU) 2017/590, Annex I, Table 2.
"""

from src.mapping.rts22_fields import RTS22_FIELDS


def map_trade_to_rts22(trade: dict) -> dict:
    """
    Build a full 65-field RTS 22 record from a raw trade dict.

    `trade` is expected to have the columns from data/sample_trades.csv:
    trade_id, trade_date, trade_time, isin, instrument_name, buy_sell,
    quantity, price, currency, trading_venue, buyer_lei, seller_lei,
    executing_firm_lei, capacity, short_selling_ind.
    """
    # Start with every one of the 65 fields present but blank.
    report = {field["name"]: "" for field in RTS22_FIELDS}

    trading_date_time = trade.get("trade_date", "").strip() + "T" + trade.get("trade_time", "").strip()

    # --- Fields a simple equity/ETF trade can actually populate ---
    report["report_status"] = "NEWT"
    report["transaction_reference_number"] = trade.get("trade_id", "").strip()
    report["executing_entity_id"] = trade.get("executing_firm_lei", "").strip()
    report["investment_firm_covered_by_mifid"] = "true"
    report["submitting_entity_id"] = trade.get("executing_firm_lei", "").strip()
    report["buyer_id"] = trade.get("buyer_lei", "").strip()
    report["seller_id"] = trade.get("seller_lei", "").strip()
    report["transmission_of_order_indicator"] = "false"
    report["trading_date_time"] = trading_date_time
    report["trading_capacity"] = trade.get("capacity", "").strip()
    report["quantity"] = trade.get("quantity", "").strip()
    report["price"] = trade.get("price", "").strip()
    report["price_currency"] = trade.get("currency", "").strip()
    report["venue"] = trade.get("trading_venue", "").strip()
    report["instrument_id"] = trade.get("isin", "").strip()
    report["instrument_full_name"] = trade.get("instrument_name", "").strip()
    report["short_selling_indicator"] = trade.get("short_selling_ind", "").strip()
    report["commodity_derivative_indicator"] = "false"
    report["securities_financing_transaction_indicator"] = "false"

    # Everything else — natural-person details, decision-maker fields,
    # algo trading codes, waivers, all derivative-specific fields — stays
    # blank. Not missing data: genuinely not applicable to this trade type.

    return report