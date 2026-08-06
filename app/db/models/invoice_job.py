import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class InvoiceJob(Base):
    __tablename__ = "invoice_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        default= uuid.uuid4, 
    )

    status: Mapped[str] = mapped_column(
        String(30), 
        nullable = False, 
        default = "pending",
    )

    idempotency_key: Mapped[str] = mapped_column(
        String (255), 
        nullable = False, 
        unique = True,
    )

    request_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=False,
    )

    file_hash : Mapped[str] = mapped_column(
        String(64),
        nullable = True, 
        unique = True, 
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message : Mapped[str | None] = mapped_column(
        String (255), 
        nullable = True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    invoice: Mapped["Invoice | None"] = relationship(
        back_populates="job"
    )

