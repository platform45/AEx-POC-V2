from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent_tools.tool_use import respond_to_session, start_session

router = APIRouter()


class SessionResponse(BaseModel):
    session_id: str
    message: str
    done: bool
    escalated: bool


class RespondRequest(BaseModel):
    input: str


@router.post("/session", response_model=SessionResponse, status_code=201)
async def create_session():
    result = await start_session()
    return SessionResponse(**result)


@router.post("/session/{session_id}/respond", response_model=SessionResponse)
async def respond(session_id: str, payload: RespondRequest):
    if not payload.input.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty.")
    result = await respond_to_session(session_id, payload.input)
    return SessionResponse(**result)
