from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import CaseContext
from app.services.embedding import get_embedding


async def search_similar_cases(query: str, limit: int = 5) -> list[dict]:
    embedding = await get_embedding(query, input_type="query")
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CaseContext)
            .order_by(CaseContext.embedding.l2_distance(embedding))
            .limit(limit)
        )
        rows = result.scalars().all()
        return [
            {
                "id": str(row.id),
                "title": row.title,
                "description": row.description,
                "raw_context": row.raw_context,
            }
            for row in rows
        ]
