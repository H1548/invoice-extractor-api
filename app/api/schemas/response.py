from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import date
from uuid import UUID, uuid4
from typing import List, Optional

class ConfidenceScores(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vendor_name: float | None
    invoice_number: float | None
    invoice_date: float | None
    due_date: float | None
    total_amount: float | None
    tax_amount: float | None
    shipping_amount: float | None
    currency: float | None
    purchase_order_number: float | None
    bank_payment_details: float | None
    line_items: float | None

class CanonicalLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str | None
    quantity: Decimal | None
    unit_price: Decimal | None
    amount: Decimal | None

class CanonicalInvoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vendor_name: str | None
    invoice_number:str | None
    invoice_date: date| None
    due_date: date| None
    total_amount: Decimal | None
    sub_total : Decimal | None
    tax_amount: Decimal | None
    shipping_amount: Decimal | None
    currency : str | None
    purchase_order_number: str | None
    line_items : list[CanonicalLineItem] | None
    bank_payment_details: str | None
    warnings: list[str]
    needs_review: bool
    confidence: ConfidenceScores
    issues: List[str] | None
