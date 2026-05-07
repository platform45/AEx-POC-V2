from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.db.models import CaseContext


async def search_similar_cases(embedding: list[float], limit: int = 5) -> list[dict]:
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
