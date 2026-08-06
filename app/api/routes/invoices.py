from fastapi import FastAPI, File, UploadFile, HTTPException,APIRouter, Header, Request, Depends
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.services.pipeline_service import Pipeline
import os
import tempfile
import asyncio
import logging
import hashlib
from typing import Annotated
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Invoice, InvoiceJob, InvoiceLineItem
from app.db.session import get_db_session
from app.domain.models.invoice import CanonicalInvoice

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    "application/pdf", 
    "image/png", 
    "image/jpeg", 
    "image/tiff"
}

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

router = APIRouter()

DbSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]

UploadedInvoice = Annotated[
    UploadFile,
    File(),
]

IdempotencyKey = Annotated[
    str,
    Header(
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
]

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global pipeline_service
#     pipeline_service = Pipeline()
#     yield

def build_invoice(
    job: InvoiceJob,
    extracted: dict,
) -> Invoice:
    invoice = Invoice(
        job=job,
        vendor_name=extracted.vendor_name,
        invoice_number=extracted.invoice_number,
        invoice_date=extracted.invoice_date,
        due_date=extracted.due_date,
        total_amount=extracted.total_amount,
        subtotal = extracted.sub_total,
        tax_amount=extracted.tax_amount,
        shipping_amount=extracted.shipping_amount,
        currency=extracted.currency,
        purchase_order_number=extracted.purchase_order_number,
        warnings=extracted.warnings,
        need_review=extracted.needs_review,
        confidence=extracted.confidence.model_dump(),
    )

    invoice.line_items = [
        InvoiceLineItem(
            line_number=line_number,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.amount
        )
        for line_number, item in enumerate(
            extracted.line_items or [],
            start=1,
        )
    ]

    return invoice

def reject_existing_job(
    job: InvoiceJob,
    request_hash: str,
) -> None:
    if job.request_hash != request_hash:
        raise HTTPException(
            status_code=409,
            detail=(
                "This idempotency key has already been used "
                "for a different file."
            ),
        )

    raise HTTPException(
        status_code=409,
        detail={
            "message": "This request has already been accepted.",
            "job_id": str(job.id),
            "status": job.status,
        },
    )


async def mark_job_failed(
    session: AsyncSession,
    job_id: UUID,
) -> None:
    async with session.begin():
        job = await session.get(
            InvoiceJob,
            job_id,
            with_for_update=True,
        )

        if job is not None:
            job.status = "failed"
            job.error_message = "pipeline failed"


@router.post("/extract", response_model=CanonicalInvoice)
async def prompt_pipeline(request: Request, file: UploadedInvoice, session: DbSession, idempotency_key: IdempotencyKey,) -> CanonicalInvoice:

    if file.content_type not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Allowed: PDF, PNG, JPEG, TIFF.")

    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400, 
            detail = "The uploaded file is empty",
        )

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The uploaded file is larger than 10 MB.",
        )

    request_hash = hashlib.sha256(content).hexdigest()

    try:
        async with session.begin():
            existing_job = await session.scalar(
                select(InvoiceJob).where(
                    InvoiceJob.idempotency_key == idempotency_key
                )
            )

            if existing_job is not None:
                reject_existing_job(existing_job, request_hash)

            job = InvoiceJob(
                idempotency_key = idempotency_key, 
                request_hash = request_hash, 
                status = "processing", 
                attempt_count = 1
            )

            session.add(job)

            await session.flush()
            job_id = job.id
    except IntegrityError:
        existing_job = await session.scalar(
            select(InvoiceJob).where(
                InvoiceJob.idempotency_key == idempotency_key
            )
        )

        if existing_job is None: 
            raise

        reject_existing_job(existing_job, request_hash)
        raise

    tmp_path = None
    
    try: 
    
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            tmp.write(content)
            tmp.close()
            tmp_path = tmp.name


            pipeline_service = request.app.state.pipeline_service

            raw_output = await asyncio.to_thread(
                    pipeline_service.process_invoice,
                    tmp_path,
                    )

            raw_output = raw_output["cannonical_output"]
            
            extracted = CanonicalInvoice.model_validate(raw_output)
            

            async with session.begin():
                job = await session.get(
                    InvoiceJob, 
                    job_id,
                    with_for_update=True, 
                )

                if job is None: 
                    raise RuntimeError(
                        f"Invoice job {job_id} no longer exists."
                    )
                invoice = build_invoice(job, extracted)

                session.add(invoice)
                job.status = "succeeded"
            return extracted 
    except Exception as error: 
        logger.exception(
            "Invoice extraction failed for job %s",
            job_id,
        )

        try:
            await mark_job_failed(session, job_id)
        except Exception: 
            logger.exception(
                "Could not mark invoice job %s as failed",
                job_id,
            )
        raise HTTPException(
            status_code= 500, 
            detail = "Invoice extraction Failed.",
        ) from error 
    
    finally:
         if (tmp_path is not None and os.path.exists(tmp_path)):
              os.remove(tmp_path)
