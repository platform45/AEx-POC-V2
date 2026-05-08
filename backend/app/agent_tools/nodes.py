import anthropic

from app.agent_tools.db_ops import fetch_device_issues, insert_issue, resolve_issue
from app.agent_tools.state import IssueResolveState
from app.core.config import settings

MAX_RETRIES = 2


def _bot(content: str) -> dict:
    return {"role": "assistant", "content": content}


# Kick off the conversation by asking for the device ID
async def prompt_device_id(state: IssueResolveState) -> IssueResolveState:
    msg = _bot("Please provide the device ID you are experiencing issues with.")
    return {**state, "messages": state.get("messages", []) + [msg]}


# Read device ID from user input and load its issue history
async def capture_device_id(state: IssueResolveState) -> IssueResolveState:
    device_id = state["user_input"].strip()
    history = await fetch_device_issues(device_id)
    return {**state, "device_id": device_id, "device_history": history}


# Prompt for the issue description, showing a history summary if one exists
async def prompt_issue(state: IssueResolveState) -> IssueResolveState:
    history = state.get("device_history", [])
    if history:
        resolved_count = sum(1 for h in history if h["resolved"])
        context = (
            f"I found {len(history)} previous issue(s) for {state['device_id']} "
            f"({resolved_count} resolved). "
        )
    else:
        context = f"No previous issues found for {state['device_id']}. "
    msg = _bot(f"{context}Please describe the current issue.")
    return {**state, "messages": state["messages"] + [msg]}


# Read issue description from user input and insert the new record
async def capture_issue(state: IssueResolveState) -> IssueResolveState:
    issue_desc = state["user_input"].strip()
    issue_id = await insert_issue(state["device_id"], issue_desc)
    return {**state, "issue_description": issue_desc, "issue_id": issue_id}


# Ask Claude to suggest a resolution using device history as context
async def build_resolution(state: IssueResolveState) -> IssueResolveState:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    history = state.get("device_history", [])
    history_lines = "\n".join(
        f"- [{'Resolved' if h['resolved'] else 'Unresolved'}] {h['issue_description']}"
        + (f" → {h['resolution_description']}" if h.get("resolution_description") else "")
        for h in history
    )

    prompt = (
        f"Device: {state['device_id']}\n"
        f"Current issue: {state['issue_description']}\n\n"
        + (f"Past issues for this device:\n{history_lines}\n\n" if history_lines else "")
        + "Suggest a concise, step-by-step resolution for this issue."
    )

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    suggestion = response.content[0].text
    retry_count = state.get("retry_count", 0) + 1
    return {**state, "suggested_resolution": suggestion, "retry_count": retry_count}


# Add the suggestion to messages and ask whether the issue is now resolved
async def prompt_resolved(state: IssueResolveState) -> IssueResolveState:
    msg = _bot(
        f"Based on the device history, here is a suggested resolution:\n\n"
        f"{state['suggested_resolution']}\n\n"
        f"Has this resolved the issue? (yes / no)"
    )
    return {**state, "messages": state["messages"] + [msg]}


# Read the yes/no answer and set the resolved flag
async def capture_resolved(state: IssueResolveState) -> IssueResolveState:
    answer = state["user_input"].strip().lower()
    resolved = answer in {"yes", "y"}
    return {**state, "resolved": resolved}


# Mark the issue resolved in the DB and close the conversation
async def finish_resolved(state: IssueResolveState) -> IssueResolveState:
    await resolve_issue(state["issue_id"], state["suggested_resolution"])
    msg = _bot("Great! The issue has been marked as resolved. Have a good day.")
    return {**state, "messages": state["messages"] + [msg], "done": True}


# Max retries exhausted – leave the record unresolved and direct to support
async def escalate(state: IssueResolveState) -> IssueResolveState:
    msg = _bot(
        "We were unable to resolve this issue automatically after several attempts. "
        "Please call support for further assistance. The issue has been logged."
    )
    return {**state, "messages": state["messages"] + [msg], "done": True, "escalated": True}


# Routing after the user's yes/no response
def route_after_resolved(state: IssueResolveState) -> str:
    if state["resolved"]:
        return "finish_resolved"
    if state.get("retry_count", 0) < MAX_RETRIES:
        return "build_resolution"
    return "escalate"
