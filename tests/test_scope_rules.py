from src.regime.scope_rules import (
    is_in_scope_eu,
    is_in_scope_uk_current,
    is_in_scope_uk_proposed,
)

UK_LISTED_EQUITY = {"trading_venue": "XLON", "asset_class": "EQUITY"}
EU_LISTED_EQUITY = {"trading_venue": "XETR", "asset_class": "EQUITY"}
FX_FORWARD_ON_EU_VENUE = {"trading_venue": "XEUR", "asset_class": "FX_DERIVATIVE"}
EQUITY_DERIVATIVE_UK_UNDERLYING = {
    "trading_venue": "XEUR",
    "asset_class": "EQUITY_DERIVATIVE",
    "underlying_traded_on_uk_venue": "true",
}
EQUITY_DERIVATIVE_EU_UNDERLYING_ONLY = {
    "trading_venue": "XEUR",
    "asset_class": "EQUITY_DERIVATIVE",
}


def test_uk_listed_equity_out_of_scope_for_eu_regime():
    assert is_in_scope_eu(UK_LISTED_EQUITY) is False


def test_eu_listed_equity_in_scope_today_but_not_under_uk_proposed():
    assert is_in_scope_uk_current(EU_LISTED_EQUITY) is True
    assert is_in_scope_uk_proposed(EU_LISTED_EQUITY) is False


def test_fx_derivative_dropped_only_under_uk_proposed():
    assert is_in_scope_eu(FX_FORWARD_ON_EU_VENUE) is True
    assert is_in_scope_uk_current(FX_FORWARD_ON_EU_VENUE) is True
    assert is_in_scope_uk_proposed(FX_FORWARD_ON_EU_VENUE) is False


def test_equity_derivative_stays_in_scope_via_uk_underlying_exception():
    assert is_in_scope_uk_proposed(EQUITY_DERIVATIVE_UK_UNDERLYING) is True


def test_equity_derivative_drops_out_without_uk_underlying_exception():
    assert is_in_scope_uk_proposed(EQUITY_DERIVATIVE_EU_UNDERLYING_ONLY) is False


def test_uk_listed_equity_in_scope_under_both_uk_regimes():
    assert is_in_scope_uk_current(UK_LISTED_EQUITY) is True
    assert is_in_scope_uk_proposed(UK_LISTED_EQUITY) is True