# Controller for the issue resolution conversation flow.
# The API layer calls start_session / respond_to_session; all graph state
# lives in the LangGraph MemorySaver keyed by session_id (thread_id).
import uuid

from app.agent_tools.graph import issue_graph
from app.agent_tools.state import IssueResolveState

_INITIAL_STATE: IssueResolveState = {
    "device_id": "",
    "device_history": [],
    "issue_description": "",
    "issue_id": None,
    "retry_count": 0,
    "suggested_resolution": "",
    "resolved": False,
    "escalated": False,
    "done": False,
    "user_input": "",
    "messages": [],
}


def _latest_bot_message(state: dict) -> str:
    # Walk backwards through messages to find the most recent assistant turn
    for msg in reversed(state.get("messages", [])):
        if msg["role"] == "assistant":
            return msg["content"]
    return ""


async def start_session() -> dict:
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    # Run graph from the start; pauses before capture_device_id
    state = await issue_graph.ainvoke(_INITIAL_STATE, config=config)

    return {
        "session_id": session_id,
        "message": _latest_bot_message(state),
        "done": False,
        "escalated": False,
    }


async def respond_to_session(session_id: str, user_input: str) -> dict:
    config = {"configurable": {"thread_id": session_id}}

    # Inject user input into the checkpointed state
    await issue_graph.aupdate_state(config, {"user_input": user_input})

    # Resume until the next interrupt or END
    state = await issue_graph.ainvoke(None, config=config)

    return {
        "session_id": session_id,
        "message": _latest_bot_message(state),
        "done": state.get("done", False),
        "escalated": state.get("escalated", False),
    }
