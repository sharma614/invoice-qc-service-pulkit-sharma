from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class LineItem:
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: float = 0.0


@dataclass
class Invoice:
    invoice_number: Optional[str] = None
    external_reference: Optional[str] = None

    seller_name: Optional[str] = None
    seller_tax_id: Optional[str] = None
    seller_address: Optional[str] = None

    buyer_name: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    buyer_address: Optional[str] = None

    invoice_date: Optional[str] = None
    due_date: Optional[str] = None

    currency: Optional[str] = None
    net_total: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None

    payment_terms: Optional[str] = None

    line_items: List[LineItem] = field(default_factory=list)

    raw_text: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "invoice_number": self.invoice_number,
            "external_reference": self.external_reference,
            "seller_name": self.seller_name,
            "seller_tax_id": self.seller_tax_id,
            "seller_address": self.seller_address,
            "buyer_name": self.buyer_name,
            "buyer_tax_id": self.buyer_tax_id,
            "buyer_address": self.buyer_address,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "currency": self.currency,
            "net_total": self.net_total,
            "tax_amount": self.tax_amount,
            "gross_total": self.gross_total,
            "payment_terms": self.payment_terms,
            "line_items": [li.__dict__ for li in self.line_items],
            "raw_text": self.raw_text,
        }
