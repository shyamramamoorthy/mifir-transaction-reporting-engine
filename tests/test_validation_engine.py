import csv

from src.mapping.field_mapper import map_trade_to_rts22
from src.validation.engine import ValidationEngine


def load_trades():
    with open("data/sample_trades.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_clean_trades_pass_with_no_errors():
    engine = ValidationEngine()
    trades = {t["trade_id"]: t for t in load_trades()}
    for trade_id in [f"TRD-00{i}" for i in range(1, 9)]:
        report = map_trade_to_rts22(trades[trade_id])
        assert engine.validate(report) == []


def test_blank_isin_is_rejected():
    engine = ValidationEngine()
    trades = {t["trade_id"]: t for t in load_trades()}
    report = map_trade_to_rts22(trades["TRD-009"])
    errors = engine.validate(report)
    assert any(e["field"] == "instrument_id" and e["rule"] == "REQUIRED" for e in errors)


def test_negative_quantity_is_rejected():
    engine = ValidationEngine()
    trades = {t["trade_id"]: t for t in load_trades()}
    report = map_trade_to_rts22(trades["TRD-010"])
    errors = engine.validate(report)
    assert any(e["field"] == "quantity" and e["rule"] == "MIN_VALUE" for e in errors)


def test_zero_price_is_rejected():
    engine = ValidationEngine()
    trades = {t["trade_id"]: t for t in load_trades()}
    report = map_trade_to_rts22(trades["TRD-012"])
    errors = engine.validate(report)
    assert any(e["field"] == "price" and e["rule"] == "MIN_VALUE" for e in errors)


def test_blank_currency_is_rejected():
    engine = ValidationEngine()
    trades = {t["trade_id"]: t for t in load_trades()}
    report = map_trade_to_rts22(trades["TRD-013"])
    errors = engine.validate(report)
    assert any(e["field"] == "price_currency" and e["rule"] == "REQUIRED" for e in errors)


def test_blank_buyer_id_is_rejected():
    engine = ValidationEngine()
    trades = {t["trade_id"]: t for t in load_trades()}
    report = map_trade_to_rts22(trades["TRD-015"])
    errors = engine.validate(report)
    assert any(e["field"] == "buyer_id" and e["rule"] == "REQUIRED" for e in errors)