"""
RTS 22 validation engine.

Applies structural and business rules to a mapped RTS 22 report (the
output of field_mapper.map_trade_to_rts22), reusing the real checksum
validators from Day 1 and the real field names from Day 2.

Deliberately scoped to what a simple on-venue equity/ETF trade actually
populates -- see docs/rts22_field_reference.md for what's conditional.
"""

from src.identifiers.lei import is_valid_lei
from src.identifiers.isin import is_valid_isin


REQUIRED_FIELDS = [
    "transaction_reference_number", "executing_entity_id", "buyer_id", "seller_id",
    "trading_date_time", "trading_capacity", "quantity", "price", "price_currency",
    "venue", "instrument_id",
]

LEI_FIELDS = ["executing_entity_id", "buyer_id", "seller_id"]

ALLOWED_VALUES = {
    "report_status": {"NEWT", "CANC"},
    "trading_capacity": {"DEAL", "MTCH", "AOTC"},
    "short_selling_indicator": {"SESH", "SSEX", "SELL", "UNDI"},
}


class ValidationEngine:
    """Validates a mapped RTS 22 report and returns a list of errors."""

    def validate(self, report: dict) -> list[dict]:
        errors = []
        errors += self._check_required(report)
        errors += self._check_lei_formats(report)
        errors += self._check_isin_format(report)
        errors += self._check_allowed_values(report)
        errors += self._check_positive_numbers(report)
        return errors

    def _check_required(self, report: dict) -> list[dict]:
        errors = []
        for field in REQUIRED_FIELDS:
            if not report.get(field, "").strip():
                errors.append({"field": field, "rule": "REQUIRED", "message": f"{field} is required"})
        return errors

    def _check_lei_formats(self, report: dict) -> list[dict]:
        # Note: buyer_id/seller_id can legitimately be a MIC, a national ID,
        # or 'INTC' per field 7/16 -- we only treat them as LEIs when they
        # aren't 'INTC'. Full type-detection (tying in national_id.py from
        # Day 3) is a future enhancement, not built yet.
        errors = []
        for field in LEI_FIELDS:
            value = report.get(field, "").strip()
            if value and value != "INTC" and not is_valid_lei(value):
                errors.append({"field": field, "rule": "FORMAT", "message": f"{field}='{value}' is not a valid LEI"})
        return errors

    def _check_isin_format(self, report: dict) -> list[dict]:
        errors = []
        value = report.get("instrument_id", "").strip()
        if value and not is_valid_isin(value):
            errors.append({"field": "instrument_id", "rule": "FORMAT", "message": f"instrument_id='{value}' is not a valid ISIN"})
        return errors

    def _check_allowed_values(self, report: dict) -> list[dict]:
        errors = []
        for field, allowed in ALLOWED_VALUES.items():
            value = report.get(field, "").strip()
            if value and value not in allowed:
                errors.append({"field": field, "rule": "ALLOWED_VALUES", "message": f"{field}='{value}' not in {sorted(allowed)}"})
        return errors

    def _check_positive_numbers(self, report: dict) -> list[dict]:
        errors = []
        for field in ["quantity", "price"]:
            value = report.get(field, "").strip()
            if value in ("", "PNDG", "NOAP"):
                continue
            try:
                if float(value) <= 0:
                    errors.append({"field": field, "rule": "MIN_VALUE", "message": f"{field} must be > 0, got '{value}'"})
            except ValueError:
                errors.append({"field": field, "rule": "FORMAT", "message": f"{field}='{value}' is not numeric"})
        return errors