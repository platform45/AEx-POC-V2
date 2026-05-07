from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CaseContext
from app.db.session import get_db
from app.services.embedding import get_embedding

router = APIRouter()


class CaseCreate(BaseModel):
    title: str
    description: str
    raw_context: dict[str, Any] = {}


class CaseResponse(BaseModel):
    id: str
    title: str
    description: str
    raw_context: dict[str, Any]
    created_at: datetime


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case(payload: CaseCreate, db: AsyncSession = Depends(get_db)):
    embedding = await get_embedding(f"{payload.title} {payload.description}")
    case = CaseContext(
        title=payload.title,
        description=payload.description,
        embedding=embedding,
        raw_context=payload.raw_context,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return CaseResponse(
        id=str(case.id),
        title=case.title,
        description=case.description,
        raw_context=case.raw_context or {},
        created_at=case.created_at,
    )


@router.get("/", response_model=list[CaseResponse])
async def list_cases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CaseContext).order_by(CaseContext.created_at.desc())
    )
    cases = result.scalars().all()
    return [
        CaseResponse(
            id=str(c.id),
            title=c.title,
            description=c.description,
            raw_context=c.raw_context or {},
            created_at=c.created_at,
        )
        for c in cases
    ]


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CaseContext).where(CaseContext.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseResponse(
        id=str(case.id),
        title=case.title,
        description=case.description,
        raw_context=case.raw_context or {},
        created_at=case.created_at,
    )


class OutcomeUpdate(BaseModel):
    outcome: Literal["resolved", "unresolved", "escalated"]


@router.patch("/{case_id}/outcome", response_model=CaseResponse)
async def update_outcome(
    case_id: UUID,
    payload: OutcomeUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CaseContext).where(CaseContext.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    updated_context = {**(case.raw_context or {})}
    updated_context["outcome"] = payload.outcome
    case.raw_context = updated_context

    await db.commit()
    await db.refresh(case)
    return CaseResponse(
        id=str(case.id),
        title=case.title,
        description=case.description,
        raw_context=case.raw_context,
        created_at=case.created_at,
    )
