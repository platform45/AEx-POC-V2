from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

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


@router.post("/", response_model=CaseResponse)
async def create_case(payload: CaseCreate):
    return CaseResponse(
        id="placeholder-id",
        title=payload.title,
        description=payload.description,
        raw_context=payload.raw_context,
    )


@router.get("/")
async def list_cases():
    return {"cases": []}


@router.get("/{case_id}")
async def get_case(case_id: str):
    return {"id": case_id, "title": "", "description": "", "raw_context": {}}
