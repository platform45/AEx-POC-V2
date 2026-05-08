# CRUD operations for the issue_resolve table
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.db.models import IssueResolve
from app.db.session import AsyncSessionLocal


# Fetch recent issues for a device, newest first
async def fetch_device_issues(device_id: str) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IssueResolve)
            .where(IssueResolve.device_id == device_id)
            .order_by(IssueResolve.created_at.desc())
            .limit(10)
        )
        rows = result.scalars().all()
        return [
            {
                "id": str(row.id),
                "issue_description": row.issue_description,
                "resolved": row.resolved,
                "resolution_description": row.resolution_description,
            }
            for row in rows
        ]


# Insert a new unresolved issue record and return its UUID string
async def insert_issue(device_id: str, issue_description: str) -> str:
    async with AsyncSessionLocal() as session:
        issue = IssueResolve(
            device_id=device_id,
            issue_description=issue_description,
        )
        session.add(issue)
        await session.commit()
        await session.refresh(issue)
        return str(issue.id)


# Mark an existing issue as resolved with the supplied resolution text
async def resolve_issue(issue_id: str, resolution_description: str) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(IssueResolve)
            .where(IssueResolve.id == issue_id)
            .values(
                resolved=True,
                resolution_description=resolution_description,
                resolved_at=datetime.now(timezone.utc),
            )
        )
        await session.commit()
