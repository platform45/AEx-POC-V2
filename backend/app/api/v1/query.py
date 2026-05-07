from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from app.services.query_agent import answer_query

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sql: str | None
    data: list[dict[str, Any]] | None


@router.post("/", response_model=QueryResponse)
async def run_query(payload: QueryRequest):
    result = await answer_query(payload.question)
    return QueryResponse(
        answer=result["answer"],
        sql=result["sql"],
        data=result["data"],
    )
