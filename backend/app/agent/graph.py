from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.agent.nodes import retrieve, suggest, execute


def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("retrieve", retrieve)
    builder.add_node("suggest", suggest)
    builder.add_node("execute", execute)

    builder.set_entry_point("retrieve")
    builder.add_edge("retrieve", "suggest")
    builder.add_edge("suggest", "execute")
    builder.add_edge("execute", END)

    checkpointer = MemorySaver()
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute"],
    )

    return graph


agent_graph = build_graph()
