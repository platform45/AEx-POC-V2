from fastapi import APIRouter

from app.api.v1.diagnostics import router as diagnostics_router
from app.api.v1.cases import router as cases_router
from app.api.v1.query import router as query_router
from app.api.v1.issues import router as issues_router

router = APIRouter()

router.include_router(diagnostics_router, prefix="/diagnostics", tags=["diagnostics"])
router.include_router(cases_router, prefix="/cases", tags=["cases"])
router.include_router(query_router, prefix="/query", tags=["query"])
router.include_router(issues_router, prefix="/issues", tags=["issues"])
