from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db, AsyncSessionLocal
from app import elastic
from app.csv_loader import load_csv_if_empty
from app.routers.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await elastic.init_index()
    async with AsyncSessionLocal() as session:
        await load_csv_if_empty(session)
    yield
    await elastic.es_client.close()


app = FastAPI(
    title="Search Service",
    description="Простой поисковик по текстам документов",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents_router)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}