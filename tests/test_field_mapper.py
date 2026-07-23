import csv


def test_maps_every_row_in_sample_trades_without_error():
    with open("data/sample_trades.csv", newline="", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    assert len(trades) > 0  # sanity check the file actually loaded

    for trade in trades:
        report = map_trade_to_rts22(trade)
        assert len(report) == 65
        assert report["transaction_reference_number"] == trade["trade_id"]




from src.mapping.field_mapper import map_trade_to_rts22


SAMPLE_TRADE = {
    "trade_id": "TRD-001",
    "trade_date": "2024-03-15",
    "trade_time": "09:31:00Z",
    "isin": "GB00B24CGK77",
    "instrument_name": "Barclays PLC Ord",
    "buy_sell": "BUYI",
    "quantity": "5000",
    "price": "189.5",
    "currency": "GBP",
    "trading_venue": "XLON",
    "buyer_lei": "213800MBWEIJDM5CU638",
    "seller_lei": "G5GSEF7VJP5I7OUK5573",
    "executing_firm_lei": "529900T8BM49AURSDO55",
    "capacity": "DEAL",
    "short_selling_ind": "UNDI",
}


def test_maps_core_fields_correctly():
    report = map_trade_to_rts22(SAMPLE_TRADE)
    assert report["transaction_reference_number"] == "TRD-001"
    assert report["instrument_id"] == "GB00B24CGK77"
    assert report["trading_date_time"] == "2024-03-15T09:31:00Z"
    assert report["price"] == "189.5"
    assert report["venue"] == "XLON"


def test_report_has_all_65_fields():
    report = map_trade_to_rts22(SAMPLE_TRADE)
    assert len(report) == 65


def test_not_applicable_fields_are_blank():
    report = map_trade_to_rts22(SAMPLE_TRADE)
    assert report["buyer_first_name"] == ""
    assert report["strike_price"] == ""
