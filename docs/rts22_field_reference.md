# RTS 22 Field Reference

Full field table from Commission Delegated Regulation (EU) 2017/590 (RTS 22),
Annex I, Table 2 — "Details to be reported in transaction reports." All fields
are mandatory unless stated otherwise. Source: legislation.gov.uk assimilated
law text (see docs/sources.md).

Format codes in brackets (e.g. `{LEI}`, `{ALPHANUM-52}`) specify the exact
data type and length ESMA requires — not our own shorthand.

## Report identification

| # | Field | Format | Notes |
|---|---|---|---|
| 1 | Report status | `NEWT` / `CANC` | New report or cancellation |
| 2 | Transaction Reference Number | `{ALPHANUM-52}` | Unique per transaction, per executing firm |
| 3 | Trading venue transaction identification code | `{ALPHANUM-52}` | Venue-generated; market side only |
| 4 | Executing entity identification code | `{LEI}` | The firm executing the transaction |
| 5 | Investment Firm covered by Directive 2014/65/EU | `true` / `false` | Is field 4 a MiFID investment firm |
| 6 | Submitting entity identification code | `{LEI}` | Firm/venue/ARM actually submitting the report |

## Buyer details (fields 7–15)

| # | Field | Format | Notes |
|---|---|---|---|
| 7 | Buyer identification code | `{LEI}` / `{MIC}` / `{NATIONAL_ID}` / `'INTC'` | Rich decision tree — see notes above |
| 8 | Country of the branch for the buyer | `{COUNTRYCODE_2}` | Only if buyer is a client |
| 9 | Buyer – first name(s) | `{ALPHANUM-140}` | Only if buyer is a natural person |
| 10 | Buyer – surname(s) | `{ALPHANUM-140}` | Natural person only |
| 11 | Buyer – date of birth | `{DATEFORMAT}` | Natural person only |
| 12 | Buyer decision maker code | `{LEI}` / `{NATIONAL_ID}` | Only if decision maker acts under power of representation |
| 13 | Buy decision maker – first name(s) | `{ALPHANUM-140}` | Natural person decision maker only |
| 14 | Buy decision maker – surname(s) | `{ALPHANUM-140}` | Natural person decision maker only |
| 15 | Buy decision maker – date of birth | `{DATEFORMAT}` | Natural person decision maker only |

## Seller details (fields 16–24)

Mirror fields 7–15 exactly, for the seller instead of the buyer (16 = Seller identification code ... 24 = Sell decision maker – date of birth).

## Transmission details

| # | Field | Format | Notes |
|---|---|---|---|
| 25 | Transmission of order indicator | `true` / `false` | Set by transmitting firm |
| 26 | Transmitting firm identification code for the buyer | `{LEI}` | |
| 27 | Transmitting firm identification code for the seller | `{LEI}` | |

## Transaction details

| # | Field | Format | Notes |
|---|---|---|---|
| 28 | Trading date time | `{DATE_TIME_FORMAT}` | To the second, at minimum, off-venue |
| 29 | Trading capacity | `DEAL` / `MTCH` / `AOTC` | Dealing on own account / matched principal / any other capacity |
| 30 | Quantity | `{DECIMAL-18/17}` (units) or `{DECIMAL-18/5}` (monetary) | |
| 31 | Quantity currency | `{CURRENCYCODE_3}` | Only if quantity is monetary |
| 32 | Derivative notional increase/decrease | `INCR` / `DECR` | Only if notional changes |
| 33 | Price | `{DECIMAL-18/13}` / `{DECIMAL-11/10}` / `{DECIMAL-18/17}` / `PNDG` / `NOAP` | Monetary, %, or basis points |
| 34 | Price Currency | `{CURRENCYCODE_3}` | |
| 35 | Net amount | `{DECIMAL-18/5}` | Debt instruments only |
| 36 | Venue | `{MIC}` (incl. `XOFF`, `XXXX` special codes) | |
| 37 | Country of the branch membership | `{COUNTRYCODE_2}` | Market side, trading venue only |
| 38 | Up-front payment | `{DECIMAL-18/5}` | Signed: positive if seller receives it |
| 39 | Up-front payment currency | `{CURRENCYCODE_3}` | |
| 40 | Complex trade component id | `{ALPHANUM-35}` | Links multi-instrument package trades |

## Instrument details (fields 41–56)

Fields 42–56 only apply when the instrument is **not** already on ESMA's reference data list and wasn't executed on a venue or SI — mostly relevant to bespoke OTC derivatives.

| # | Field | Format | Notes |
|---|---|---|---|
| 41 | Instrument identification code | `{ISIN}` | |
| 42 | Instrument full name | `{ALPHANUM-350}` | |
| 43 | Instrument classification | `{CFI_CODE}` | ISO 10962 Classification of Financial Instruments |
| 44 | Notional currency 1 | `{CURRENCYCODE_3}` | |
| 45 | Notional currency 2 | `{CURRENCYCODE_3}` | Multi-currency swaps |
| 46 | Price multiplier | `{DECIMAL-18/17}` | Units of underlying per contract |
| 47 | Underlying instrument code | `{ISIN}` | |
| 48 | Underlying index name | `{INDEX}` / `{ALPHANUM-25}` | |
| 49 | Term of the underlying index | `{INTEGER-3}` + `DAYS`/`WEEK`/`MNTH`/`YEAR` | |
| 50 | Option type | `PUTO` / `CALL` / `OTHR` | |
| 51 | Strike price | as field 33, or `PNDG` | |
| 52 | Strike price currency | `{CURRENCYCODE_3}` | |
| 53 | Option exercise style | `EURO` / `AMER` / `ASIA` / `BERM` / `OTHR` | |
| 54 | Maturity date | `{DATEFORMAT}` | Debt instruments |
| 55 | Expiry date | `{DATEFORMAT}` | Derivatives |
| 56 | Delivery type | `PHYS` / `CASH` / `OPTL` | |

## Trader, algorithms, waivers and indicators (fields 57–65)

| # | Field | Format | Notes |
|---|---|---|---|
| 57 | Investment decision within firm | `{NATIONAL_ID}` (person) / `{ALPHANUM-50}` (algo) | |
| 58 | Country of branch supervising investment decision | `{COUNTRYCODE_2}` | N/A if decision made by algo |
| 59 | Execution within firm | `{NATIONAL_ID}` (person) / `{ALPHANUM-50}` (algo) | |
| 60 | Country of branch supervising execution | `{COUNTRYCODE_2}` | N/A if executed by algo |
| 61 | Waiver indicator | `RFPT` / `NLIQ` / `OILQ` / `PRIC` / `SIZE` / `ILQD` | Pre-trade transparency waiver used |
| 62 | Short selling indicator | `SESH` / `SSEX` / `SELL` / `UNDI` | **Note: our old project incorrectly used `SHOR` — not a real value** |
| 63 | OTC post-trade indicator | `BENC`/`ACTX`/`LRGS`/`ILQD`/`SIZE`/`CANC`/`AMND`/`SDIV`/`RPRI`/`DUPL`/`TNCP`/`TPAC`/`XFPH` | Which post-trade deferral/flag category applies |
| 64 | Commodity derivative indicator | `true` / `false` | Risk-reducing per Article 57 |
| 65 | Securities financing transaction indicator | `true` / `false` | Exempt from SFTR reporting |