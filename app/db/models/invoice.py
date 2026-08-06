import uuid
from datetime import datetime
from decimal import Decimal 

from sqlalchemy import ForeignKey, Date, Numeric, Text, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            primary_key=True, 
            default= uuid.uuid4, 
        )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoice_jobs.id"),
        nullable=False,
        unique= True, 
    )

    vendor_name : Mapped[str | None] = mapped_column(
        String (50), 
        nullable = True,
        default= "vendor Name...", 
    )

    invoice_number : Mapped[str | None] = mapped_column(
        String (60), 
        nullable = True, 
    )

    invoice_date : Mapped[datetime | None] = mapped_column(
        Date,
        nullable= True, 

    )

    due_date : Mapped[datetime | None] = mapped_column(
        Date, 
        nullable = True
    )

    total_amount : Mapped[Decimal | None] = mapped_column(
            Numeric(12,2), 
            nullable = True,
        )    

    subtotal : Mapped[Decimal | None] = mapped_column(
        Numeric(12,2), 
        nullable = True,
    )

    tax_amount : Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), 
        nullable = True, 
    )

    shipping_amount : Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), 
        nullable = True,
    )

    currency : Mapped[str | None] = mapped_column(
        String(3), 
        nullable = True, 
    )

    purchase_order_number : Mapped[str] = mapped_column(
        String(50), 
        nullable= False
    )

    warnings : Mapped[list[str] | None] = mapped_column(
        MutableList.as_mutable(ARRAY(Text)),
        nullable=True,
        default=list,
    )

    need_review : Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
    )

    confidence : Mapped[dict[str, float | None]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
    )

    issues  : Mapped[list[str] | None] = mapped_column(
            MutableList.as_mutable(ARRAY(Text)),
            nullable=True,
            default=list,
        )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable = False, 
        server_default=func.now(),
    )

    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable = False, 
        server_default=func.now(),
    )

    job: Mapped["InvoiceJob"] = relationship(
        back_populates="invoice"
    )

    line_items: Mapped[list["InvoiceLineItem"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InvoiceLineItem.line_number",
        lazy="selectin",
    )
