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