from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import CaseContext
from app.db.session import get_db
from app.services.embedding import get_embedding
from app.services.nms_client import NMSClient
from app.services.vector_search import search_similar_cases

router = APIRouter()


def _nms_client() -> NMSClient:
    return NMSClient(base_url=settings.NMS_BASE_URL)


class DiagnosticRequest(BaseModel):
    device_id: str
    issue_description: str


class DiagnosticResponse(BaseModel):
    case_id: str
    device_id: str
    status: str
    raw_context: dict[str, Any]
    similar_cases: list[dict[str, Any]]
    created_at: datetime


@router.post("/run", response_model=DiagnosticResponse, status_code=201)
async def run_diagnostic(
    payload: DiagnosticRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. Fetch live device status from NMS (stubbed until NMS_BASE_URL is live)
    nms_result: dict[str, Any] = {}
    if settings.NMS_BASE_URL:
        try:
            client = _nms_client()
            nms_result = await client.get_device_status(payload.device_id)
        except Exception:
            nms_result = {"error": "NMS unreachable"}

    # 2. Build the context object
    raw_context: dict[str, Any] = {
        "inputs": {
            "device_id": payload.device_id,
            "issue": payload.issue_description,
        },
        "actions": [],
        "results": nms_result,
        "outcome": "open",
    }

    # 3. Embed and store the new diagnostic session as a case context
    embed_text = f"{payload.issue_description} device:{payload.device_id}"
    embedding = await get_embedding(embed_text, input_type="document")

    case = CaseContext(
        title=f"Diagnostic – {payload.device_id}",
        description=payload.issue_description,
        embedding=embedding,
        raw_context=raw_context,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)

    # 4. Retrieve similar past cases to surface to the engineer
    similar = await search_similar_cases(payload.issue_description, limit=5)

    return DiagnosticResponse(
        case_id=str(case.id),
        device_id=payload.device_id,
        status="open",
        raw_context=raw_context,
        similar_cases=similar,
        created_at=case.created_at,
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
