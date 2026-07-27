# MiFIR Transaction Reporting Engine

A MiFIR RTS 22 transaction reporting engine, built field by field from
primary regulatory sources rather than summaries — ESMA's RTS 22 legal
text, the FCA's live 2025/26 reform consultation, and the ISO standards
behind LEI and ISIN checksums.

## Why this exists

Built as a structured way to learn MiFIR transaction reporting in depth:
not by reading about the rules, but by encoding them, testing them against
real reference data, and hitting the genuine edge cases (natural-person
identifier hierarchies, same-day correction workflows, live UK/EU
divergence) that a summary article skips over. Every validation rule in
the code cites the regulation clause it implements — see
`docs/sources.md` for the full source list.

This is a learning project, not production reporting software. It doesn't
connect to an ARM, doesn't handle the full 65-field set for every
instrument type, and the UK regime it models is partly a live proposal
(see the caveat in `docs/uk_eu_divergence.md`). What it does demonstrate
is real domain fluency: the actual field-level mechanics, correction
workflow, and cross-jurisdiction differences a transaction reporting
practitioner works with.

## What's in here

| Path | What it does |
|---|---|
| `src/identifiers/lei.py` | LEI checksum validation (ISO 17442, MOD 97-10) |
| `src/identifiers/isin.py` | ISIN checksum validation (ISO 6166, Luhn) |
| `src/identifiers/national_id.py` | Natural-person identifier hierarchy (RTS 22 Article 6, Annex II) |
| `src/mapping/rts22_fields.py` | The full 65-field RTS 22 Annex I Table 2 field list |
| `src/mapping/field_mapper.py` | Maps a raw trade into a full 65-field RTS 22 report |
| `src/validation/engine.py` | Validates a mapped report: required fields, formats, allowed values, positive numbers |
| `src/lifecycle/report_status.py` | T+1 deadline logic and the CANC-then-NEWT correction workflow |
| `src/export/xml_writer.py` | Builds ISO 20022 (`auth.016.001.01`) XML for a report |
| `src/regime/scope_rules.py` | UK vs EU reporting-scope divergence, including the FCA's proposed reforms |
| `src/regime/cli.py` | Command-line tool to check scope for a sample trade under a given regime |

## Documentation

- `docs/rts22_field_reference.md` — the full 65-field reference table
- `docs/uk_eu_divergence.md` — where UK and EU rules actually differ, and what's still just proposed
- `docs/LEARNING_LOG.md` — a day-by-day build diary: what was learned, what broke, what was fixed
- `docs/sources.md` — every primary source used, with links

## Running it
python3 -m pytest -v
51 tests, covering checksum validation against real reference LEIs/ISINs,
full field mapping, the identifier hierarchy, the validation engine, the
lifecycle/export logic, the UK/EU scope rules, and one end-to-end
integration test tying the pipeline together.

Check whether a sample trade is in scope under a given regime:
python3 -m src.regime.cli SCOPE-003 --regime eu
python3 -m src.regime.cli SCOPE-003 --regime uk_proposed

## Status

All 65 RTS 22 fields
are modelled; a subset (the fields a simple on-venue equity/ETF trade
actually populates) are wired end-to-end through mapping, validation, and
XML export. See `docs/LEARNING_LOG.md` for the day-by-day build log.


To take it through the full pipeline
python3 -m scripts.run_pipeline TRD-001

Trade
   ↓
Field Mapper
   ↓
Validation Engine
   ↓
ISO 20022 XML