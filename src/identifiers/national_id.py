"""
Natural person identifier construction, per RTS 22 Article 6 and Annex II.

Article 6(1): a natural person is identified by concatenating their
nationality's ISO 3166-1 alpha-2 code with a national client identifier
(see ANNEX_II_PRIORITY below).

Article 6(4)-(5): where Annex II specifies CONCAT (no suitable national ID
exists for that country), the identifier is instead built from:
  (a) date of birth, format YYYYMMDD
  (b) first 5 characters of the first name
  (c) first 5 characters of the surname
Accents, apostrophes, hyphens, punctuation and spaces are stripped first;
everything is upper-cased; anything shorter than 5 characters is padded
with '#'.

Source: Commission Delegated Regulation (EU) 2017/590, Article 6;
Annex II (ESMA/2016/1064).

Known simplification: Article 6(5) also says "prefixes to names shall be
excluded" (e.g. "van", "Mc") -- not implemented here, since it requires a
maintained, culture-specific list of prefixes rather than a fixed rule.
"""

import unicodedata


def _clean_name_part(name: str) -> str:
    """Strip accents, punctuation and spaces, per Article 6(5)."""
    normalized = unicodedata.normalize("NFKD", name)
    letters_only = "".join(ch for ch in normalized if ch.isalpha() and ch.isascii())
    return letters_only.upper()


def _pad_to_five(text: str) -> str:
    """Take the first 5 characters, padding with '#' if shorter."""
    return text[:5].ljust(5, "#")


def build_concat(date_of_birth: str, first_name: str, surname: str) -> str:
    """
    Build the CONCAT natural-person identifier per Article 6(4)-(5).

    date_of_birth: string already in YYYYMMDD format
    first_name, surname: as given -- accents/punctuation/spaces are
                          cleaned up internally
    """
    first_clean = _pad_to_five(_clean_name_part(first_name))
    surname_clean = _pad_to_five(_clean_name_part(surname))
    return f"{date_of_birth}{first_clean}{surname_clean}"


# Annex II, National client identifiers for natural persons (ESMA/2016/1064).
# Each value is the ordered list of identifier types, highest priority first.
# NOTE: a few rows (flagged below) had ambiguous column alignment in the
# source PDF extraction and should be spot-checked against the original
# before relying on them for anything beyond illustration.
ANNEX_II_PRIORITY = {
    "AT": ["CONCAT"],
    "BE": ["Belgian National Number", "CONCAT"],
    "BG": ["Bulgarian Personal Number", "CONCAT"],
    "CY": ["National Passport Number", "CONCAT"],
    "CZ": ["National identification number (Rodné číslo)", "Passport Number", "CONCAT"],
    "DE": ["Personal Identity Card Number (Personalausweisnummer)", "National Passport Number", "CONCAT"],  # extraction ambiguous -- verify against source PDF
    "DK": ["Personal identity code", "CONCAT"],
    "EE": ["Estonian Personal Identification Code (Isikukood)", "CONCAT"],
    "ES": ["Tax identification number (Código de identificación fiscal)", "CONCAT"],
    "FI": ["Personal identity code", "CONCAT"],
    "FR": ["CONCAT"],
    "GB": ["UK National Insurance number", "CONCAT"],
    "GR": ["10 digit investor share number", "CONCAT"],
    "HR": ["Personal Identification Number (OIB)", "CONCAT"],
    "HU": ["CONCAT"],
    "IE": ["CONCAT"],
    "IS": ["Personal Identity Code (Kennitala)", "National Passport Number"],
    "IT": ["Fiscal code (Codice fiscale)", "CONCAT"],
    "LI": ["National Passport Number", "National Identity Card Number", "CONCAT"],
    "LT": ["Personal code (Asmens kodas)", "National Passport Number", "CONCAT"],
    "LU": ["CONCAT"],
    "LV": ["Personal code (Personas kods)", "CONCAT"],
    "MT": ["National Identification Number", "National Passport Number"],
    "NL": ["National Passport Number", "National identity card number", "CONCAT"],
    "NO": ["11 digit personal id (Foedselsnummer)", "CONCAT"],
    "PL": ["National Identification Number (PESEL)", "Tax Number"],
    "PT": ["Tax number (Número de Identificação Fiscal)", "National Passport Number", "CONCAT"],
    "RO": ["National Identification Number (Cod Numeric Personal)", "National Passport Number", "CONCAT"],
    "SE": ["Personal identity number", "CONCAT"],
    "SI": ["Personal Identification Number (EMŠO)", "CONCAT"],
    "SK": ["Personal number (Rodné číslo)", "National Passport Number", "CONCAT"],
    "ALL_OTHER": ["National Passport Number", "CONCAT"],
}

# EEA member states for Article 6(3) purposes -- EU member states plus
# Iceland, Liechtenstein, Norway. GB is deliberately excluded: although it
# still appears as a row in Annex II (this regulation predates Brexit),
# the UK left the EEA and its own onshored version of this rule now
# applies separately.
EEA_COUNTRY_CODES = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR",
    "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL",
    "PT", "RO", "SE", "SI", "SK",
    "IS", "LI", "NO",
}


def select_reporting_nationality(nationalities: list[str]) -> str:
    """
    Given the ISO 3166-1 alpha-2 nationality codes for a person, pick
    which one to use for reporting, per Article 6(3).

    Rule from the text: if the person holds one or more EEA nationalities,
    use the alphabetically-first EEA code. Where a person has EEA and
    non-EEA nationality, the EEA one is used.

    Note: the regulation does not specify a tie-break when someone holds
    multiple *non-EEA* nationalities and no EEA one at all. Alphabetical
    order here is our own reasonable default, not drawn from the text --
    flagged rather than presented as settled.
    """
    eea_nationalities = sorted(n for n in nationalities if n in EEA_COUNTRY_CODES)
    if eea_nationalities:
        return eea_nationalities[0]
    return sorted(nationalities)[0]


def get_identifier_type(nationality: str) -> str:
    """
    Return the highest-priority Annex II identifier type for a nationality.
    Falls back to the 'all other countries' row for any nationality not
    explicitly listed in Annex II (i.e. any non-EEA country).
    """
    priorities = ANNEX_II_PRIORITY.get(nationality, ANNEX_II_PRIORITY["ALL_OTHER"])
    return priorities[0]
