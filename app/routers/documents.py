from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app import crud, elastic
from app.schemas import SearchResponse, DocumentOut, DeleteResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Текстовый поисковый запрос"),
    session: AsyncSession = Depends(get_session),
):
    ids = await elastic.search_documents(q, size=20)
    docs = await crud.get_documents_by_ids(session, ids)
    docs.sort(key=lambda d: d.created_date, reverse=True)
    return SearchResponse(
        total=len(docs),
        items=[DocumentOut.model_validate(d) for d in docs],
    )


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete(doc_id: int, session: AsyncSession = Depends(get_session)):
    deleted = await crud.delete_document(session, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return DeleteResponse(id=doc_id, deleted=True)