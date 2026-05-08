from typing import TypedDict, Optional


class IssueResolveState(TypedDict):
    # Collected during the conversation
    device_id: str
    device_history: list[dict]
    issue_description: str
    issue_id: Optional[str]

    # Resolution tracking
    retry_count: int
    suggested_resolution: str
    resolved: bool
    escalated: bool
    done: bool

    # Conversation flow
    user_input: str
    messages: list[dict]  # {"role": "assistant" | "user", "content": str}
