import re
from datetime import datetime
from typing import Optional, List

AMOUNT_RE = re.compile(r"(-?\d{1,3}(?:[,\.]\d{3})*(?:[\.,]\d+)?|\d+[\.,]\d+)")
DATE_PATTERNS = [
    (re.compile(r"\d{4}-\d{2}-\d{2}"), "%Y-%m-%d"),
    (re.compile(r"\d{2}[\./]\d{2}[\./]\d{4}"), "%d.%m.%Y"),
    (re.compile(r"\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}"), "%d %B %Y"),
]
CURRENCY_CODES = ["EUR", "USD", "GBP", "INR"]

def parse_amount(s: Optional[str]) -> Optional[float]:
    """Parse a string into a float amount, handling various separators."""
    if not s:
        return None
    # Remove non-breaking spaces and white-space
    s = s.replace('\u00A0', '').strip()
    # Basic cleanup: remove commas often used as thousand separators
    s = s.replace(',', '')
    try:
        return float(s)
    except (ValueError, TypeError):
        try:
            m = AMOUNT_RE.search(s)
            if m:
                return float(m.group(1).replace(',', ''))
        except (ValueError, TypeError):
            return None
    return None

def parse_date(s: Optional[str]) -> Optional[str]:
    """Parse various date formats and return as ISO string (YYYY-MM-DD)."""
    if not s:
        return None
    
    # Try ISO first
    try:
        return datetime.fromisoformat(s).date().isoformat()
    except (ValueError, TypeError):
        pass

    # Try patterns
    for regex, fmt in DATE_PATTERNS:
        m = regex.search(s)
        if m:
            try:
                return datetime.strptime(m.group(0), fmt).date().isoformat()
            except ValueError:
                continue
    
    # Fallback to general formats if regex didn't catch it or matched but failed strptime
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except (ValueError, TypeError):
            continue
            
    return None

def find_currency(text: str) -> Optional[str]:
    """Find currency code or symbol in text."""
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
