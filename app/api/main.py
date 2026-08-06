from fastapi import FastAPI
# from app.api.routes.invoices import lifespan
from app.api.routes import invoices
from app.api.routes import health
from app.services.pipeline_service import Pipeline
from app.db.session import engine
from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        "Event loop:",
        type(asyncio.get_running_loop()).__name__,
    )
    app.state.pipeline_service = Pipeline()

    try: 
        yield
    finally:
        await engine.dispose()

app = FastAPI(title= "Autonomous Invoice Extractor",lifespan=lifespan)
app.include_router(invoices.router)
app.include_router(health.router)
