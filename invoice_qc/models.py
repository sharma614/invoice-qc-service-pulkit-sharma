from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: float = 0.0

class Invoice(BaseModel):
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

    line_items: List[LineItem] = Field(default_factory=list)

    raw_text: Optional[str] = None

    def to_dict(self) -> dict:
        return self.model_dump()
