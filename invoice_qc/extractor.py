import re
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
except Exception:
    pdfplumber = None

AMOUNT_RE = re.compile(r"(-?\d{1,3}(?:[,\.]\d{3})*(?:[\.,]\d+)?|\d+[\.,]\d+)")
INVOICE_NUMBER_PATTERNS = [r"Invoice\s*No[:#\s]*([A-Z0-9\-_/]+)", r"Invoice\s*#[:\s]*([A-Z0-9\-_/]+)", r"Invoice\s*Number[:\s]*([A-Z0-9\-_/]+)", r"Inv\.?\s*No[:\s]*([A-Z0-9\-_/]+)"]
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{2}[\./]\d{2}[\./]\d{4}|\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})")
CURRENCY_CODES = ["EUR", "USD", "GBP", "INR"]


def extract_text_from_pdf(path: Path) -> str:
    text = ""
    if pdfplumber:
        try:
            with pdfplumber.open(str(path)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
                text = "\n".join(pages)
                return text
        except Exception:
            pass

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(path))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        text = "\n".join(pages)
        return text
    except Exception:
        return ""


def _first_match(patterns, text: str) -> Optional[str]:
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def parse_amount(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    s = s.replace('\u00A0', '').strip()
    s = s.replace(',', '')
    try:
        return float(s)
    except Exception:
        try:
            m = AMOUNT_RE.search(s)
            if m:
                return float(m.group(1).replace(',', ''))
        except Exception:
            return None
    return None


def find_currency(text: str) -> Optional[str]:
    for code in CURRENCY_CODES:
        if re.search(r"\b" + re.escape(code) + r"\b", text):
            return code
    if "€" in text:
        return "EUR"
    if "$" in text:
        return "USD"
    if "₹" in text or "Rs." in text:
        return "INR"
    return None


def parse_invoice_text(text: str, filename: str = None) -> Dict:
    invoice_number = _first_match(INVOICE_NUMBER_PATTERNS, text)
    
    if not invoice_number:
        m = re.search(r"Bestellung\s+([A-Z0-9]+)", text, flags=re.IGNORECASE)
        if m:
            invoice_number = m.group(1).strip()
    if not invoice_number:
        m = re.search(r"AUFNR([A-Z0-9]+)", text, flags=re.IGNORECASE)
        if m:
            invoice_number = "AUFNR" + m.group(1).strip()

    invoice_date = None
    due_date = None
    dates = DATE_RE.findall(text)
    parsed_dates = []
    for d in dates:
        try:
            if re.match(r"\d{4}-\d{2}-\d{2}", d):
                parsed = datetime.strptime(d, "%Y-%m-%d").date()
            elif re.match(r"\d{2}[\./]\d{2}[\./]\d{4}", d):
                parsed = datetime.strptime(d, "%d.%m.%Y").date()
            else:
                parsed = datetime.strptime(d, "%d %B %Y").date()
            parsed_dates.append(parsed.isoformat())
        except Exception:
            continue
    if parsed_dates:
        invoice_date = parsed_dates[0]
        if len(parsed_dates) > 1:
            due_date = parsed_dates[-1]

    seller_name = None
    buyer_name = None

    m = re.search(r"Seller[:\s\n-]{0,10}([^\n]{2,80})", text, flags=re.IGNORECASE)
    if m:
        seller_name = m.group(1).strip()
    m = re.search(r"Bill(?:ed)?\s*To[:\s\n-]{0,10}([^\n]{2,80})", text, flags=re.IGNORECASE)
    if m:
        buyer_name = m.group(1).strip()
    
    if not seller_name:
        m = re.search(r"im\s+Auftrag\s+von\s+\d+\s*\n([^\n]{2,80})", text, flags=re.IGNORECASE)
        if m:
            seller_name = m.group(1).strip()
    
    if not buyer_name:
        m = re.search(r"Kundenanschrift\s*\n([^\n]{2,80})", text, flags=re.IGNORECASE)
        if m:
            buyer_name = m.group(1).strip()

    net_total = None
    tax_amount = None
    gross_total = None

    def find_amount_by_label(label_patterns):
        for lp in label_patterns:
            m = re.search(lp + r"\s*[:\s]\s*([\d\.,\s\u00A0-]+)", text, flags=re.IGNORECASE)
            if m:
                return parse_amount(m.group(1))
        return None

    net_total = find_amount_by_label([r"Net\s+Total", r"Subtotal", r"Amount\s+excl\.?\s+tax", r"Net amount", r"Gesamtwert(?!\s+inkl)"])
    tax_amount = find_amount_by_label([r"Tax\s+Amount", r"VAT", r"Sales\s+Tax", r"MwSt"])
    gross_total = find_amount_by_label([r"Total\s+Amount", r"Amount\s+incl\.?\s+tax", r"Grand\s+Total", r"Invoice\s+Total", r"Gesamtwert\s+inkl\.?\s+MwSt"])

    if gross_total is None:
        amounts = AMOUNT_RE.findall(text)
        if amounts:
            gross_total = parse_amount(amounts[-1])

    currency = find_currency(text)

    line_items = []
    header_match = re.search(r"Description[\s\S]{0,200}?Total", text, flags=re.IGNORECASE)
    if header_match:
        block = header_match.group(0)
        lines = block.splitlines()[1:]
        for ln in lines:
            m = AMOUNT_RE.search(ln[::-1])
            if m:
                last_amt_match = AMOUNT_RE.findall(ln)
                if last_amt_match:
                    try:
                        amt = parse_amount(last_amt_match[-1])
                        desc = re.sub(r"[\d\.,]","", ln).strip()
                        if desc and amt is not None:
                            line_items.append({"description": desc, "line_total": amt})
                    except Exception:
                        continue

    result = {
        "invoice_number": invoice_number or (Path(filename).stem if filename else None),
        "external_reference": None,
        "seller_name": seller_name,
        "seller_tax_id": None,
        "seller_address": None,
        "buyer_name": buyer_name,
        "buyer_tax_id": None,
        "buyer_address": None,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "currency": currency,
        "net_total": net_total,
        "tax_amount": tax_amount,
        "gross_total": gross_total,
        "payment_terms": None,
        "line_items": line_items,
    }
    return result


def extract_from_dir(pdf_dir: str) -> List[Dict]:
    p = Path(pdf_dir)
    invoices = []
    for f in sorted(p.glob("*.pdf")):
        text = extract_text_from_pdf(f)
        parsed = parse_invoice_text(text, filename=str(f))
        invoices.append(parsed)
    return invoices


def save_json(data, path: str):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("usage: extractor.py <pdf-dir> <out.json>")
    else:
        arr = extract_from_dir(sys.argv[1])
        save_json(arr, sys.argv[2])
