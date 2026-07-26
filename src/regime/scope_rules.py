"""
Determines whether a trade falls within scope for MiFIR transaction
reporting under a given regime.

Source: FCA CP25/32 "Improving the UK transaction reporting regime"
(21 November 2025) -- paragraphs 1.6, 4.49, 4.83-4.96. Consultation
closed 20 February 2026; the FCA's policy statement and final rules
are expected in the second half of 2026 and were NOT published as of
July 2026. The "proposed" regime below models what CP25/32 proposes,
not a rule currently in force.
"""

UK_VENUES = {"XLON"}
EU_VENUES = {"XETR", "XPAR", "XAMS", "XEUR"}
# Venues outside both sets (e.g. XSWX - Switzerland, XNYS - US) are
# third-country venues. MiFIR's "traded on a trading venue" (TOTV) test
# only reaches EU/UK venues, so instruments listed only on a third-country
# venue are out of scope under every regime modelled here.


def is_in_scope_eu(trade: dict) -> bool:
    """EU MiFIR, Article 26(2): reportable if traded on an EU trading venue."""
    return trade["trading_venue"] in EU_VENUES


def is_in_scope_uk_current(trade: dict) -> bool:
    """
    Current, in-force UK MiFIR. Retained EU law carried the EU venue test
    over after Brexit, so UK OR EU venues both count today -- this is the
    Brexit-era artifact CP25/32 proposes to remove.
    """
    return trade["trading_venue"] in UK_VENUES or trade["trading_venue"] in EU_VENUES


def is_in_scope_uk_proposed(trade: dict) -> bool:
    """
    Proposed UK MiFIR under FCA CP25/32 -- not yet in force.

    Two changes from the current UK test:
    1. FX derivatives are removed from scope entirely, regardless of venue
       (CP25/32 paras 4.83-4.96) -- UK EMIR already captures this data.
    2. The venue test narrows to UK venues only (CP25/32 para 1.6), except
       a derivative not itself traded on a UK venue is still reportable if
       its underlying is traded on a UK venue (CP25/32 para 4.49).
    """
    if trade.get("asset_class") == "FX_DERIVATIVE":
        return False

    if trade["trading_venue"] in UK_VENUES:
        return True

    return bool(trade.get("underlying_traded_on_uk_venue"))