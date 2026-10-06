from elasticsearch import AsyncElasticsearch
from app.config import settings

es_client = AsyncElasticsearch(settings.elastic_url)

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "text": {"type": "text"},
        }
    }
}


async def init_index():
    if not await es_client.indices.exists(index=settings.elastic_index):
        await es_client.indices.create(
            index=settings.elastic_index, body=INDEX_MAPPING
        )


async def index_document(doc_id: int, text: str):
    await es_client.index(
        index=settings.elastic_index,
        id=doc_id,
        document={"id": doc_id, "text": text},
        refresh=True,
    )


async def delete_document(doc_id: int):
    await es_client.options(ignore_status=404).delete(
        index=settings.elastic_index,
        id=doc_id,
        refresh=True,
    )


async def search_documents(query: str, size: int = 20) -> list[int]:
    if not query.strip():
        return []
    resp = await es_client.search(
        index=settings.elastic_index,
        query={"match": {"text": query}},
        size=size,
    )
    return [hit["_source"]["id"] for hit in resp["hits"]["hits"]]