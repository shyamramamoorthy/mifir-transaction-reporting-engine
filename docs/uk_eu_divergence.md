# UK vs EU MiFIR transaction reporting — where they diverge

This tracks concrete divergence between the EU and UK transaction reporting
regimes, encoded in `src/regime/scope_rules.py`. Every rule below is
traceable to a primary source — no assumptions.

## Status note (as of July 2026)

The "UK proposed" regime described here is **not yet in force**. It reflects
the FCA's consultation paper CP25/32, "Improving the UK transaction
reporting regime" (published 21 November 2025, consultation closed
20 February 2026). The FCA's policy statement and final rules are expected
in the second half of 2026, with an implementation period of roughly 18
months after that. Until that policy statement lands, the "UK current"
regime below is what's actually in force.

## The three regimes

| | Venue test | FX derivatives |
|---|---|---|
| EU (current) | Traded on an EU trading venue | In scope |
| UK (current, in force) | Traded on a UK **or** EU trading venue | In scope |
| UK (proposed, CP25/32) | Traded on a UK trading venue (with one exception, below) | Out of scope entirely |

## Why UK-current includes EU venues

When the UK onshored EU law after Brexit, the transaction reporting rules
were copied across largely unchanged — including the EU venue test. Nobody
deliberately decided UK firms should keep reporting on EU-venue-only
instruments; it's a byproduct of the "copy first, diverge later" approach
Brexit took to financial services law. CP25/32 paragraph 1.6 is the FCA
now actually diverging: narrowing the test to UK venues only, and dropping
an estimated 6 million EU-venue-only instruments from scope.

## The underlying-instrument exception (CP25/32 para 4.49)

A derivative that isn't itself traded on a UK venue is still reportable
under the proposed UK regime if its *underlying* is traded on a UK venue.
This stops firms from being able to dodge reporting on, say, a Barclays
equity option just by listing it on a European exchange.

## FX derivatives carved out entirely (CP25/32 paras 4.83–4.96)

Unlike the venue-scope narrowing, this isn't a venue test at all — FX
derivatives drop out of UK MiFIR reporting regardless of where they trade.
The FCA's stated reasoning: UK EMIR already collects equivalent data on FX
derivatives, so MiFIR reporting duplicates it without adding much value for
market abuse detection.

## Sources

- FCA CP25/32, "Improving the UK transaction reporting regime" (21 Nov
  2025): https://www.fca.org.uk/publication/consultation/cp25-32.pdf —
  paragraphs 1.6, 4.49, 4.83–4.96
- MiFIR Article 26(2) (EU venue test):
  https://www.legislation.gov.uk/eur/2014/600/article/26