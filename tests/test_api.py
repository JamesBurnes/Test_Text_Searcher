import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import AsyncSessionLocal, init_db
from app import elastic, crud


@pytest.mark.asyncio
async def test_full_flow():
    await init_db()
    await elastic.init_index()

    async with AsyncSessionLocal() as session:
        await crud.create_document(
            session,
            rubrics=["test"],
            text="уникальное словосочетание zzzzz",
            created_date=datetime.utcnow(),
        )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/documents/search", params={"q": "zzzzz"})
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1

        doc_id = data["items"][0]["id"]
        r = await ac.delete(f"/documents/{doc_id}")
        assert r.status_code == 200
        assert r.json()["deleted"] is True

        r = await ac.delete(f"/documents/{doc_id}")
        assert r.status_code == 404