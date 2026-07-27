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

### Full RTS 22 field model
- Sourced the actual legal text: Commission Delegated Regulation (EU) 2017/590, Annex I, Table 2 (legislation.gov.uk assimilated law text), cross-checked fields 64-65 against FCA guidance
- Found and fixed a real bug from the original project: short selling indicator field used an invented code `SHOR` — the real RTS 22 values are `SESH`/`SSEX`/`SELL`/`UNDI`
- Learned the real buyer/seller identification model: not a single buy/sell flag, but separate, richly-conditional identification fields (LEI, MIC, national ID, or 'INTC') for both buyer and seller on every report
- Learned that most of RTS 22's 65 fields are conditional — a simple on-venue equity trade legitimately leaves 35+ fields blank; fields 42-56 only apply to instruments not already in ESMA's reference data
- Built: `docs/rts22_field_reference.md` (full field table), `src/mapping/rts22_fields.py` (machine-readable version), `src/mapping/field_mapper.py`
- Learned Python: list comprehensions, dict comprehensions, `csv.DictReader`
- All 18 tests passing, including a full sweep of every row in the sample dataset


## Day 3

### Natural person identifiers (Article 6 & Annex II)
- Learned the real model: a natural person's identifier is nationality code + national ID concatenated, not the national ID alone
- Learned the CONCAT fallback construction exactly: DOB (YYYYMMDD) + first 5 chars of first name + first 5 chars of surname, accents/punctuation/spaces stripped, upper-cased, padded with '#' if short
- Learned Article 6(3)'s nationality tie-break for dual nationals (EEA takes priority; alphabetically first if multiple EEA)
- Noticed GB still appears in Annex II because the table predates Brexit -- live example of UK/EU regulatory divergence
- Learned Python: `unicodedata.normalize()` for accent stripping, `str.ljust()` for padding
- Built: `src/identifiers/national_id.py`
- Caveat logged honestly: a couple of Annex II rows (Germany especially) had ambiguous PDF-extraction formatting, flagged in code comments rather than guessed at; the non-EEA tie-break rule is our own default, not specified in the text
- All 27 tests passing

## Day 4

### Validation engine
- Learned Python: classes (`class ValidationEngine:`, `self`, methods vs standalone functions) — chosen because Day 6 will need multiple configured instances (UK vs EU rule sets)
- Built `src/validation/engine.py`: REQUIRED, FORMAT (reusing lei.py/isin.py directly — first real payoff of Day 1's work), ALLOWED_VALUES, and MIN_VALUE checks
- Fixed a real data-quality issue: several "clean" sample trades still had placeholder or checksum-invalid LEIs from earlier project versions — replaced with real, verified LEIs (HSBC, BNP Paribas, two IBM entities) so the happy path is actually meaningful
- Hit and fixed a copy-paste data bug independently of the code: one row (`TRD-001` seller LEI) didn't take on manual edit twice; resolved by replacing the whole CSV file rather than patching in place
- Logged two honest known gaps rather than hiding them: `TRD-011`'s original test intent (invalid `buy_sell`) no longer applies under the corrected data model; `TRD-014`'s bad venue code isn't yet caught because real MIC-registry validation isn't built
- All 33 tests passing

## Day 5

Built the lifecycle and export pieces of the engine.

**Report lifecycle (`src/lifecycle/report_status.py`)**
- MiFIR Article 26(1) sets a T+1 deadline: reports must reach the NCA by the end of the next working day after the trade. `next_working_day_deadline()` adds a day then skips forward over Saturday/Sunday.
- There's no "amend" status in MiFIR reporting. To correct a report, you cancel the original (CANC) and submit a fresh one (NEWT) — `correct_report()` returns both in that order.

**XML export (`src/export/xml_writer.py`)**
- Learned `xml.etree.ElementTree`: `ET.Element` for a root tag, `ET.SubElement(parent, tag)` to nest children, `.text` to set content, `ET.tostring()` to serialize.
- Used the real ESMA ISO 20022 tag names (`auth.016.001.01` schema) from the Technical Reporting Instructions — TxId, ExctgPty, Buyr/AcctOwnr/Id/LEI, TradVn, etc. — rather than inventing plausible-looking tags.
- A cancellation record uses a `<Cxl>` block with just enough fields to identify the report; a new report uses a `<New>` block with the full trade detail. Confirmed this structurally by testing that `<Pric>` and `<TradVn>` never appear in a cancellation.

**Tests:** 43 passing (39 + 4 new for the XML writer).

**Source:** MiFIR Article 26(1) (T+1 deadline); ESMA/2016/1521 Technical Reporting Instructions, section 6.2 (auth.016.001.01 schema tags).


## Day 6

Built the UK vs EU regime divergence engine — the trickiest day so far,
because the "divergence" isn't settled law yet.

**What I learned about the regulatory landscape:**
- UK MiFIR today still covers instruments traded on EU venues, not just UK
  ones — a leftover of how Brexit onshored EU law wholesale rather than
  redesigning it.
- The FCA's CP25/32 consultation (Nov 2025) proposes narrowing that scope
  to UK venues only, and removing FX derivatives from UK reporting
  entirely. This is a live, unfinished process — consultation closed
  Feb 2026, final rules expected H2 2026, not yet published as of today.
- Encoding "this is proposed, not current" directly in code comments and
  docs, rather than presenting it as settled fact, felt like the right
  discipline — same as flagging an assumption in a BRD before it gets
  mistaken for a confirmed requirement.

**Python concept: `argparse`**
- Built `src/regime/cli.py` as an actual command-line tool:
  `python3 -m src.regime.cli SCOPE-003 --regime uk_proposed`
- `argparse.ArgumentParser`, `.add_argument()` with `choices=`, and
  `parser.parse_args()` — turns a script into something runnable with
  flags instead of hardcoded values.

**Design decision:** kept new scope-check data in its own file
(`data/regime_scope_examples.csv`) rather than extending
`sample_trades.csv`. Scope ("is this reportable at all") and validation
("is this filled in correctly") are genuinely different regulatory
questions, and it avoided touching a file three days of tests already
depend on.

**Tests:** 49 passing (43 + 6 new for scope_rules.py).

**Source:** FCA CP25/32 (21 Nov 2025), paragraphs 1.6, 4.49, 4.83–4.96.

## Day 7

Capstone day: no new domain rules, just making sure the six days of work
actually hold together as one thing.

**Integration test (`tests/test_integration.py`)**
- Learned the difference between a unit test (checks one function alone,
  with hand-built input) and an integration test (checks that separately
  built pieces actually work together end-to-end).
- Took a real trade from `data/sample_trades.csv` through the full
  pipeline: `map_trade_to_rts22` → `ValidationEngine.validate` →
  `build_transaction_xml`, and confirmed a broken trade gets caught by
  validation *before* it would ever reach XML export — which is the
  actual point of having validation as a separate step.

**README rewrite**
- Turned the Day 1 stub into a real front door: what the project is, why
  it exists, a module map, how to run everything, and an honest status
  section (which fields are wired end-to-end vs. just modelled).
- Added an explicit "this is a learning project, not production reporting
  software" line — the value here is demonstrated field-level fluency,
  not a claim that this could plug into an ARM.

**Commit history review**
- Looked back over the week's commits as a body of work: each one scoped
  to a single day's topic, message describing what changed and why,
  rather than one giant end-of-week commit. That history is itself part
  of what's being demonstrated.

**Tests:** 51 passing, all verified via fresh `git clone` after every
day's push — nothing in this repo has ever been taken on faith.

## Day 8

Closed the loop on the reporting lifecycle: everything up to now submitted
reports; nothing read what came back.

**Status advice parsing (`src/feedback/status_parser.py`)**
- Learned to parse XML, not just build it: `ET.fromstring()` to load an
  existing document, then `.find()`/`.findall()` to search it.
- The wrinkle: our XML declares a default namespace, so every search path
  needs a `namespaces` dict (`{"ns": "urn:iso:..."}`) and an `ns:` prefix
  on each tag — a bare tag name silently matches nothing.
- Test fixture is ESMA's own worked example from their Technical Reporting
  Instructions, not invented data — including a typo in ESMA's own
  document (`TrasnactionFile1`). Good reminder that primary sources aren't
  infallible either.

**Reconciliation (`src/feedback/reconcile.py`)**
- The single most useful thing in this day's source material (ESMA
  paragraph 111): if a submitted transaction doesn't appear in the status
  advice feedback at all, it was accepted. The ARM only reports back on
  transactions with something to say. Easy to get backwards if you didn't
  know to look for it.

**Tests:** 61 passing (51 + 10 new for status parsing and reconciliation).

**Source:** ESMA/2016/1521 Technical Reporting Instructions, section 6.3
(paragraphs 100–114).

## Day 9

Closed the loop from rejection back to correction — the last piece of the
submit → validate → export → get feedback → remediate lifecycle.

**Remediation (`src/feedback/remediation.py`)**
- Deliberately did NOT try to auto-fix a rejected trade. A rejection like
  "instrument not valid in reference data" needs a human (or an upstream
  system) to work out the actual correct value — no code can infer that
  from the rejection message alone.
- What's genuinely mechanical: building the CANC half of the CANC/NEWT
  pair from Day 5, since that only needs identifiers already on hand
  (reference number, executing/submitting entity). The module automates
  exactly that, and explicitly flags what still needs human judgment
  rather than pretending to close a loop it can't actually close.
- This felt like the right instinct to practice deliberately: knowing
  where automation genuinely ends and a person needs to take over is as
  much a part of good delivery as knowing where it can be extended.

**Tests:** 64 passing (61 + 3 new for remediation).

**Source:** builds directly on ESMA/2016/1521 section 6.3 (Day 8) and the
CANC/NEWT correction workflow (Day 5) — no new primary source needed.