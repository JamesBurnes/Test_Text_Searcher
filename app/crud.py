from datetime import datetime
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document
from app import elastic


async def get_count(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(Document)) or 0


async def create_document(
    session: AsyncSession,
    rubrics: list[str],
    text: str,
    created_date: datetime,
) -> Document:
    doc = Document(rubrics=rubrics, text=text, created_date=created_date)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    await elastic.index_document(doc.id, doc.text)
    return doc


async def get_documents_by_ids(session: AsyncSession, ids: list[int]) -> list[Document]:
    if not ids:
        return []
    result = await session.execute(select(Document).where(Document.id.in_(ids)))
    docs = {d.id: d for d in result.scalars().all()}
    return [docs[i] for i in ids if i in docs]


async def delete_document(session: AsyncSession, doc_id: int) -> bool:
    result = await session.execute(delete(Document).where(Document.id == doc_id))
    await session.commit()
    await elastic.delete_document(doc_id)
    return result.rowcount > 0