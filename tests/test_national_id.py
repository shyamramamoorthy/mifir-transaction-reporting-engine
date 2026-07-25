from src.identifiers.national_id import build_concat, ANNEX_II_PRIORITY
from src.identifiers.national_id import select_reporting_nationality, get_identifier_type


def test_build_concat_pads_short_names():
    # First name "Jo" (2 chars) padded with #, surname has apostrophe/hyphen stripped
    result = build_concat("19850312", "Jo", "O'Brien-Smith")
    assert result == "19850312JO###OBRIE"


def test_build_concat_strips_accents():
    result = build_concat("19900101", "José", "Núñez")
    assert result == "19900101JOSE#NUNEZ"


def test_build_concat_no_padding_needed():
    result = build_concat("19750630", "Anna-Maria", "Al")
    assert result == "19750630ANNAMAL###"


def test_annex_ii_has_fallback_for_all_other_countries():
    assert "ALL_OTHER" in ANNEX_II_PRIORITY
    assert ANNEX_II_PRIORITY["ALL_OTHER"][0] == "National Passport Number"

    from src.identifiers.national_id import select_reporting_nationality, get_identifier_type


def test_select_nationality_prefers_eea_when_mixed():
    assert select_reporting_nationality(["US", "DE"]) == "DE"


def test_select_nationality_picks_alphabetically_first_eea():
    assert select_reporting_nationality(["FR", "AT", "IE"]) == "AT"


def test_select_nationality_falls_back_for_non_eea_only():
    assert select_reporting_nationality(["US", "JP"]) == "JP"


def test_get_identifier_type_known_country():
    assert get_identifier_type("BE") == "Belgian National Number"


def test_get_identifier_type_unknown_country_falls_back():
    assert get_identifier_type("US") == "National Passport Number"
