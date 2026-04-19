from typing import List, Dict, Any, Tuple, Optional, Set
from datetime import datetime
from collections import Counter, defaultdict

from . import models, config
from .utils import parsing

settings = config.settings


# _parse_iso_date removed in favor of parsing.parse_date


def validate_invoice(inv: models.Invoice, seen_keys: Set[Tuple[Optional[str], Optional[str], Optional[str]]]) -> Tuple[bool, List[str]]:
    errors = []

    if not inv.invoice_number:
        errors.append("missing_field: invoice_number")
    if not inv.invoice_date:
        errors.append("missing_field: invoice_date")
    if not inv.seller_name:
        errors.append("missing_field: seller_name")
    if not inv.buyer_name:
        errors.append("missing_field: buyer_name")

    currency = inv.currency
    if currency and currency not in settings.SUPPORTED_CURRENCIES:
        errors.append("invalid_format: currency")

    inv_date_str = parsing.parse_date(inv.invoice_date)
    due_date_str = parsing.parse_date(inv.due_date)
    
    if inv.invoice_date and not inv_date_str:
        errors.append("invalid_format: invoice_date")
    if inv.due_date and not due_date_str:
        errors.append("invalid_format: due_date")

    inv_date = datetime.fromisoformat(inv_date_str).date() if inv_date_str else None
    due_date = datetime.fromisoformat(due_date_str).date() if due_date_str else None

    for fld in ("net_total", "tax_amount", "gross_total"):
        val = getattr(inv, fld)
        if val is not None:
            try:
                if float(val) < 0:
                    errors.append(f"invalid_value: {fld}_negative")
            except (ValueError, TypeError):
                errors.append(f"invalid_format: {fld}")

    net = inv.net_total
    tax = inv.tax_amount
    gross = inv.gross_total

    if net is not None and tax is not None and gross is not None:
        if abs((net + tax) - gross) > settings.TOLERANCE_TOTALS:
            errors.append("business_rule_failed: totals_mismatch")

    items = inv.line_items
    if items and net is not None:
        try:
            s = sum(i.line_total for i in items)
            if abs(s - net) > settings.TOLERANCE_LINEITEMS:
                errors.append("business_rule_failed: lineitems_sum_mismatch")
        except (ValueError, TypeError):
            errors.append("invalid_format: line_items")

    if inv_date and due_date:
        if due_date < inv_date:
            errors.append("business_rule_failed: due_before_invoice")

    dup_key = (inv.invoice_number, inv.seller_name, inv.invoice_date)
    if dup_key in seen_keys:
        errors.append("anomaly: duplicate_invoice")
    else:
        seen_keys.add(dup_key)

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_all(invoices: List[models.Invoice]) -> Dict[str, Any]:
    seen = set()
    results = []
    counter = Counter()
    valid_count = 0
    for inv in invoices:
        inv_id = inv.invoice_number or inv.external_reference or "<unknown>"
        is_valid, errors = validate_invoice(inv, seen)
        if is_valid:
            valid_count += 1
        for e in errors:
            counter[e] += 1
        results.append({"invoice_id": inv_id, "is_valid": is_valid, "errors": errors})

    summary = {
        "total_invoices": len(invoices),
        "valid_invoices": valid_count,
        "invalid_invoices": len(invoices) - valid_count,
        "error_counts": dict(counter),
    }
    return {"results": results, "summary": summary}


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) < 2:
        print("usage: validator.py <invoices.json>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        raw_invoices = json.load(fh)
    invoices = [models.Invoice(**i) for i in raw_invoices]
    out = validate_all(invoices)
    print(json.dumps(out["summary"], indent=2))
