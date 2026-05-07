from typing import TypedDict, Any


class AgentState(TypedDict):
    issue_description: str
    retrieved_cases: list[dict[str, Any]]
    suggested_actions: list[str]
    approved_actions: list[str]
    execution_results: list[dict[str, Any]]
