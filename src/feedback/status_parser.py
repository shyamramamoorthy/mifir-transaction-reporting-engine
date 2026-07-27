"""
Parses an ISO 20022 status advice message (auth.031.001.01) -- the message
an NCA/ARM sends back after processing a submitted transaction report file.

Source: ESMA/2016/1521 Technical Reporting Instructions, section 6.3
(paragraphs 100-114), including the worked XML example at paragraph 110.
"""

import xml.etree.ElementTree as ET

NAMESPACE = "urn:iso:std:iso:20022:tech:xsd:auth.031.001.01"
NS = {"ns": NAMESPACE}


def parse_status_advice(xml_string: str) -> dict:
    root = ET.fromstring(xml_string)
    msg_sts_advc = root.find("ns:FinInstrmRptgStsAdvc/ns:MsgStsAdvc", NS)

    report_status = msg_sts_advc.find("ns:MsgSts/ns:RptSts", NS).text

    records_per_status = {}
    for entry in msg_sts_advc.findall("ns:MsgSts/ns:Sttstcs/ns:NbOfRcrdsPerSts", NS):
        count = int(entry.find("ns:DtldNbOfTxs", NS).text)
        status = entry.find("ns:DtldSts", NS).text
        records_per_status[status] = count

    total_records_element = msg_sts_advc.find("ns:MsgSts/ns:Sttstcs/ns:TtlNbOfRcrds", NS)
    total_records = int(total_records_element.text) if total_records_element is not None else None

    transaction_feedback = []
    for record in msg_sts_advc.findall("ns:RcrdSts", NS):
        reference = record.find("ns:OrgnlRcrdId", NS).text
        status = record.find("ns:Sts", NS).text
        errors = []
        for rule in record.findall("ns:VldtnRule", NS):
            errors.append({
                "code": rule.find("ns:Id", NS).text,
                "description": rule.find("ns:Desc", NS).text,
            })
        transaction_feedback.append({
            "reference": reference,
            "status": status,
            "errors": errors,
        })

    return {
        "report_status": report_status,
        "total_records": total_records,
        "records_per_status": records_per_status,
        "transaction_feedback": transaction_feedback,
    }