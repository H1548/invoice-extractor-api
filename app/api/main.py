from fastapi import FastAPI
from app.api.routes.invoices import lifespan
from app.api.routes import invoices
from app.api.routes import health

app = FastAPI(title= "Autonomous Invoice Extractor",lifespan=lifespan)
app.include_router(invoices.router)
app.include_router(health.router)