from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CaseContext
from app.db.session import get_db
from app.services.vector_search import search_similar_cases

router = APIRouter()


class DiagnosticRequest(BaseModel):
    device_id: str
    issue_description: str


class DiagnosticResponse(BaseModel):
    device_id: str
    status: str
    result: dict


@router.post("/run", response_model=DiagnosticResponse)
async def run_diagnostic(payload: DiagnosticRequest):
    similar_cases = await search_similar_cases(payload.issue_description, limit=5)
    return DiagnosticResponse(
        device_id=payload.device_id,
        status="complete",
        result={"similar_cases": similar_cases},
    )


@router.get("/{device_id}")
async def get_diagnostic(device_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CaseContext)
        .where(CaseContext.raw_context["inputs"]["device_id"].astext == device_id)
        .order_by(CaseContext.created_at.desc())
    )
    cases = result.scalars().all()
    return {
        "device_id": device_id,
        "diagnostics": [
            {
                "id": str(c.id),
                "title": c.title,
                "description": c.description,
                "raw_context": c.raw_context,
                "created_at": c.created_at.isoformat(),
            }
            for c in cases
        ],
    }
