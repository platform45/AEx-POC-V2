import voyageai
from app.core.config import settings

# voyage-4 outputs 1024-dimensional vectors by default.
EMBEDDING_MODEL = "voyage-4"
EMBEDDING_DIM = 1024

_client: voyageai.AsyncClient | None = None


def _get_client() -> voyageai.AsyncClient:
    global _client
    if _client is None:
        _client = voyageai.AsyncClient(api_key=settings.VOYAGE_API_KEY)
    return _client


async def get_embedding(text: str, input_type: str = "document") -> list[float]:
    """
    input_type="document" for content being stored,
    input_type="query" for search queries.
    """
    client = _get_client()
    result = await client.embed([text], model=EMBEDDING_MODEL, input_type=input_type)
    return result.embeddings[0]
