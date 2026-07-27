"""
Reconciles our own submitted transaction reference numbers against a
parsed status advice message.

Source: ESMA/2016/1521 Technical Reporting Instructions, paragraph 111:
if a submitted transaction reference number does NOT appear in the status
advice message's per-transaction feedback at all, it is implicitly
accepted -- the ARM/NCA only reports back on transactions with something
to say (pending, rejected, or explicitly re-confirmed accepted).
"""


def reconcile(submitted_references: list, parsed_status_advice: dict) -> dict:
    feedback_by_reference = {
        item["reference"]: item for item in parsed_status_advice["transaction_feedback"]
    }

    results = {}
    for reference in submitted_references:
        if reference in feedback_by_reference:
            results[reference] = feedback_by_reference[reference]
        else:
            results[reference] = {"reference": reference, "status": "ACPT", "errors": []}

    return results