"""
Streamlit dashboard for the MiFIR RTS 22 transaction reporting engine.

Three tabs, each covering a stage of the pipeline built across Days 1-9:
1. Trade pipeline    -- map a sample trade, validate it, export ISO 20022 XML
2. Regime scope      -- check UK/EU reporting scope for a sample instrument
3. Feedback & remediation -- parse a status advice message, reconcile it
   against submitted reports, and see what action each one needs

Run locally with: streamlit run streamlit_app.py
"""

import csv

import streamlit as st

from src.mapping.field_mapper import map_trade_to_rts22
from src.validation.engine import ValidationEngine
from src.export.xml_writer import build_transaction_xml
from src.regime.scope_rules import (
    is_in_scope_eu,
    is_in_scope_uk_current,
    is_in_scope_uk_proposed,
)
from src.feedback.status_parser import parse_status_advice
from src.feedback.reconcile import reconcile
from src.feedback.remediation import determine_remediation_actions


st.set_page_config(page_title="MiFIR RTS 22 Transaction Reporting Engine", layout="wide")

st.title("MiFIR RTS 22 transaction reporting engine")
st.caption(
    "A learning project, not production reporting software. Every validation "
    "rule and regime distinction is traceable to a primary source -- see "
    "docs/sources.md in the repo. Built to learn MiFIR transaction reporting "
    "field by field, not from summaries."
)

tab_pipeline, tab_regime, tab_feedback = st.tabs(
    ["Trade pipeline", "Regime scope", "Feedback & remediation"]
)


def load_csv_rows(path: str) -> list:
    with open(path) as f:
        return list(csv.DictReader(f))


# --- Tab 1: trade pipeline -------------------------------------------------
with tab_pipeline:
    st.subheader("Map, validate, and export a sample trade")

    trades = load_csv_rows("data/sample_trades.csv")
    trade_ids = [t["trade_id"] for t in trades]
    selected_id = st.selectbox("Sample trade", trade_ids)
    raw_trade = next(t for t in trades if t["trade_id"] == selected_id)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Raw trade**")
        st.json(raw_trade)

    report = map_trade_to_rts22(raw_trade)
    errors = ValidationEngine().validate(report)

    with col2:
        st.markdown("**Validation result**")
        if errors:
            st.error(f"REJECTED -- {len(errors)} error(s)")
            for error in errors:
                st.write(f"[{error['rule']}] `{error['field']}`: {error['message']}")
        else:
            st.success("PASSED validation")

    if not errors:
        st.markdown("**ISO 20022 XML (auth.016.001.01)**")
        st.code(build_transaction_xml(report), language="xml")


# --- Tab 2: regime scope -----------------------------------------------
with tab_regime:
    st.subheader("UK vs EU reporting scope")
    st.caption(
        "The 'UK proposed' regime models the FCA's CP25/32 consultation, "
        "which is not yet in force -- see docs/uk_eu_divergence.md."
    )

    scope_examples = load_csv_rows("data/regime_scope_examples.csv")
    scope_ids = [t["trade_id"] for t in scope_examples]
    selected_scope_id = st.selectbox("Sample instrument", scope_ids)
    scope_trade = next(t for t in scope_examples if t["trade_id"] == selected_scope_id)

    st.write(f"**{scope_trade['description']}** — venue `{scope_trade['trading_venue']}`, "
             f"asset class `{scope_trade['asset_class']}`")

    regimes = {
        "EU (current)": is_in_scope_eu(scope_trade),
        "UK (current, in force)": is_in_scope_uk_current(scope_trade),
        "UK (proposed, CP25/32)": is_in_scope_uk_proposed(scope_trade),
    }

    cols = st.columns(3)
    for col, (regime_name, in_scope) in zip(cols, regimes.items()):
        with col:
            st.markdown(f"**{regime_name}**")
            if in_scope:
                st.success("IN SCOPE")
            else:
                st.error("OUT OF SCOPE")


# --- Tab 3: feedback and remediation ----------------------------------------
with tab_feedback:
    st.subheader("Status advice feedback and remediation")
    st.caption(
        "Parses a real ESMA-published status advice example (auth.031.001.01) "
        "and reconciles it against a small set of reports we 'submitted'."
    )

    with open("data/sample_status_advice.xml") as f:
        parsed = parse_status_advice(f.read())

    st.markdown("**Overall report status**")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Report status", parsed["report_status"])
    m2.metric("Total records", parsed["total_records"])
    m3.metric("Rejected", parsed["records_per_status"].get("RJCT", 0))
    m4.metric("Pending", parsed["records_per_status"].get("PDNG", 0))

    # A small fixed set of "our" submitted reports -- mirrors what the test
    # suite uses, standing in for reports we'd have generated in Tab 1.
    submitted_reports = {
        "00987654321009876543TXN13": {
            "transaction_reference_number": "00987654321009876543TXN13",
            "executing_entity_id": "529900T8BM49AURSDO55",
            "submitting_entity_id": "529900T8BM49AURSDO55",
        },
        "00987654321009876543TXN151": {
            "transaction_reference_number": "00987654321009876543TXN151",
            "executing_entity_id": "529900T8BM49AURSDO55",
            "submitting_entity_id": "529900T8BM49AURSDO55",
        },
        "TRD-001": {
            "transaction_reference_number": "TRD-001",
            "executing_entity_id": "529900T8BM49AURSDO55",
            "submitting_entity_id": "529900T8BM49AURSDO55",
        },
    }

    reconciled = reconcile(list(submitted_reports.keys()), parsed)
    actions = determine_remediation_actions(reconciled, submitted_reports)

    st.markdown("**Reconciliation and remediation**")
    for action in actions:
        with st.expander(f"{action['reference']} — {action['action']}"):
            st.write(action["note"])
            if action["action"] == "CANCEL_AND_RESUBMIT":
                st.write("Rejection reason(s):")
                for reason in action["rejection_reasons"]:
                    st.write(f"- `{reason['code']}`: {reason['description']}")
                st.write("Auto-generated cancellation record:")
                st.json(action["cancellation"])