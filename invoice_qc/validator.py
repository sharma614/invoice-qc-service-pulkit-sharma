from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import Counter, defaultdict

TOLERANCE_TOTALS = 0.5
TOLERANCE_LINEITEMS = 1.0


def _parse_iso_date(s: str):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d %B %Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
    return None


def validate_invoice(inv: Dict, seen_keys: set) -> Tuple[bool, List[str]]:
    errors = []

    if not inv.get("invoice_number"):
        errors.append("missing_field: invoice_number")
    if not inv.get("invoice_date"):
        errors.append("missing_field: invoice_date")
    if not inv.get("seller_name"):
        errors.append("missing_field: seller_name")
    if not inv.get("buyer_name"):
        errors.append("missing_field: buyer_name")

    currency = inv.get("currency")
    if currency and currency not in ("EUR", "USD", "GBP", "INR"):
        errors.append("invalid_format: currency")

    inv_date = _parse_iso_date(inv.get("invoice_date"))
    due_date = _parse_iso_date(inv.get("due_date"))
    if inv.get("invoice_date") and not inv_date:
        errors.append("invalid_format: invoice_date")
    if inv.get("due_date") and not due_date:
        errors.append("invalid_format: due_date")

    for fld in ("net_total", "tax_amount", "gross_total"):
        val = inv.get(fld)
        if val is not None:
            try:
                if float(val) < 0:
                    errors.append(f"invalid_value: {fld}_negative")
            except Exception:
                errors.append(f"invalid_format: {fld}")

    try:
        net = float(inv.get("net_total")) if inv.get("net_total") is not None else None
    except Exception:
        net = None
    try:
        tax = float(inv.get("tax_amount")) if inv.get("tax_amount") is not None else None
    except Exception:
        tax = None
    try:
        gross = float(inv.get("gross_total")) if inv.get("gross_total") is not None else None
    except Exception:
        gross = None

    if net is not None and tax is not None and gross is not None:
        if abs((net + tax) - gross) > TOLERANCE_TOTALS:
            errors.append("business_rule_failed: totals_mismatch")

    items = inv.get("line_items") or []
    if items and net is not None:
        try:
            s = sum(float(i.get("line_total", 0)) for i in items)
            if abs(s - net) > TOLERANCE_LINEITEMS:
                errors.append("business_rule_failed: lineitems_sum_mismatch")
        except Exception:
            errors.append("invalid_format: line_items")

    if inv_date and due_date:
        if due_date < inv_date:
            errors.append("business_rule_failed: due_before_invoice")

    dup_key = (inv.get("invoice_number"), inv.get("seller_name"), inv.get("invoice_date"))
    if dup_key in seen_keys:
        errors.append("anomaly: duplicate_invoice")
    else:
        seen_keys.add(dup_key)

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_all(invoices: List[Dict]) -> Dict[str, Any]:
    seen = set()
    results = []
    counter = Counter()
    valid_count = 0
    for inv in invoices:
        inv_id = inv.get("invoice_number") or inv.get("external_reference") or "<unknown>"
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
        invoices = json.load(fh)
    out = validate_all(invoices)
    print(json.dumps(out["summary"], indent=2))
