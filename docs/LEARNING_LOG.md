# Learning Log

Running notes on what was built and learned, written as we go.

---

## Day 1

### LEI checksum (ISO 17442 / ISO 7064 MOD 97-10)
- Learned: LEI = 20 chars = 18 identifying chars + 2 check digits (MOD 97-10 checksum, same family as IBAN)
- Learned the algorithm: letters → numbers (A=10...Z=35, via `ord(char) - 55`), whole 20-char code treated as one big number, valid LEI has remainder 1 when divided by 97
- Learned Python: functions (`def`), docstrings, `for` loops over strings, `ord()`, arbitrary-precision integers, `if __name__ == "__main__":`
- Learned pytest: `assert`, test auto-discovery via `test_` prefix, `conftest.py` as a root marker enabling imports, running via `python3 -m pytest -v`
- Built: `src/identifiers/lei.py`, `tests/test_identifiers.py`
- Validated against two real GLEIF-registered LEIs (Barclays Bank PLC, Deutsche Bank AG) — all 5 tests passing

### Git basics
- Learned the four-zone git model: working directory → staging → local commit → remote (GitHub)
- Commands used: `git clone`, `git status`, `git add`, `git commit -m`, `git push`
- Hit and fixed: GitHub rejects account passwords for git over HTTPS (removed 2021) — needed a Personal Access Token instead, generated at github.com/settings/tokens with `repo` scope

### ISIN checksum (ISO 6166, Luhn algorithm)
- Learned: ISIN = 12 chars = 2-letter country code + 9-char NSIN + 1 numeric check digit
- Learned the algorithm ("Double-Add-Double", per ISO 6166 Annex C): same letter→number trick as LEI, then Luhn — double every other digit from the right, reduce two-digit results (sum the digits, equivalent to -9), sum everything, check digit rounds up to the next multiple of 10
- Learned Python: `enumerate()` (loop with a running index), `[::-1]` slicing shorthand for reversing a string
- Built: `src/identifiers/isin.py`
- Validated against real ISINs: Apple Inc. (canonical worked example for this algorithm), plus HSBC/Deutsche Bank from the original project's sample data — turned out those were genuinely valid ISINs even though the old project never checked the checksum

### Bug caught: duplicate test function names
- LEI and ISIN test sections both independently defined `test_rejects_wrong_length()` in the same file
- Python silently let the second definition overwrite the first — no error, no warning; the LEI test just vanished (pytest reported 10 tests, not the expected 11)
- Lesson: prefix test names with what they test (`test_lei_...`, `test_isin_...`) to prevent silent collisions as the suite grows
- Fixed by renaming to `test_lei_rejects_wrong_length` / `test_isin_rejects_wrong_length` — 11 tests, all passing

## Day 2

## Day 2

### Full RTS 22 field model
- Sourced the actual legal text: Commission Delegated Regulation (EU) 2017/590, Annex I, Table 2 (legislation.gov.uk assimilated law text), cross-checked fields 64-65 against FCA guidance
- Found and fixed a real bug from the original project: short selling indicator field used an invented code `SHOR` — the real RTS 22 values are `SESH`/`SSEX`/`SELL`/`UNDI`
- Learned the real buyer/seller identification model: not a single buy/sell flag, but separate, richly-conditional identification fields (LEI, MIC, national ID, or 'INTC') for both buyer and seller on every report
- Learned that most of RTS 22's 65 fields are conditional — a simple on-venue equity trade legitimately leaves 35+ fields blank; fields 42-56 only apply to instruments not already in ESMA's reference data
- Built: `docs/rts22_field_reference.md` (full field table), `src/mapping/rts22_fields.py` (machine-readable version), `src/mapping/field_mapper.py`
- Learned Python: list comprehensions, dict comprehensions, `csv.DictReader`
- All 18 tests passing, including a full sweep of every row in the sample dataset