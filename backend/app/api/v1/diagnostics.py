from fastapi import APIRouter
from pydantic import BaseModel

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
    return DiagnosticResponse(
        device_id=payload.device_id,
        status="pending",
        result={},
    )


@router.get("/{device_id}")
async def get_diagnostic(device_id: str):
    return {"device_id": device_id, "diagnostics": []}
