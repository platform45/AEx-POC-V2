from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent_tools.state import IssueResolveState
from app.agent_tools.nodes import (
    build_resolution,
    capture_device_id,
    capture_issue,
    capture_resolved,
    escalate,
    finish_resolved,
    prompt_device_id,
    prompt_issue,
    prompt_resolved,
    route_after_resolved,
)


def build_graph() -> StateGraph:
    builder = StateGraph(IssueResolveState)

    builder.add_node("prompt_device_id", prompt_device_id)
    builder.add_node("capture_device_id", capture_device_id)
    builder.add_node("prompt_issue", prompt_issue)
    builder.add_node("capture_issue", capture_issue)
    builder.add_node("build_resolution", build_resolution)
    builder.add_node("prompt_resolved", prompt_resolved)
    builder.add_node("capture_resolved", capture_resolved)
    builder.add_node("finish_resolved", finish_resolved)
    builder.add_node("escalate", escalate)

    builder.set_entry_point("prompt_device_id")

    # Linear flow up to the first resolution attempt
    builder.add_edge("prompt_device_id", "capture_device_id")
    builder.add_edge("capture_device_id", "prompt_issue")
    builder.add_edge("prompt_issue", "capture_issue")
    builder.add_edge("capture_issue", "build_resolution")
    builder.add_edge("build_resolution", "prompt_resolved")
    builder.add_edge("prompt_resolved", "capture_resolved")

    # After yes/no: resolve, retry, or escalate
    builder.add_conditional_edges(
        "capture_resolved",
        route_after_resolved,
        {
            "finish_resolved": "finish_resolved",
            "build_resolution": "build_resolution",
            "escalate": "escalate",
        },
    )

    builder.add_edge("finish_resolved", END)
    builder.add_edge("escalate", END)

    # Pause before each node that requires user input
    checkpointer = MemorySaver()
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["capture_device_id", "capture_issue", "capture_resolved"],
    )

    return graph


issue_graph = build_graph()
