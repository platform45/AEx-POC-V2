from app.agent.state import AgentState
from app.services.vector_search import search_similar_cases
from app.core.config import settings
import anthropic


async def retrieve(state: AgentState) -> AgentState:
    cases = await search_similar_cases(state["issue_description"], limit=5)
    return {**state, "retrieved_cases": cases}


async def suggest(state: AgentState) -> AgentState:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    context = "\n".join(
        f"- {c.get('title', '')}: {c.get('description', '')}"
        for c in state["retrieved_cases"]
    )

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Issue: {state['issue_description']}\n\n"
                    f"Similar past cases:\n{context}\n\n"
                    "Suggest a numbered list of diagnostic actions to resolve this issue."
                ),
            }
        ],
    )

    text = message.content[0].text
    actions = [line.strip() for line in text.splitlines() if line.strip()]
    return {**state, "suggested_actions": actions}


async def execute(state: AgentState) -> AgentState:
    results = []
    for action in state["approved_actions"]:
        results.append({"action": action, "status": "executed", "output": ""})
    return {**state, "execution_results": results}
