import anthropic
from sqlalchemy import text
from app.core.config import settings
from app.db.session import AsyncSessionLocal

# Schema description passed to Claude so it understands the database structure
DB_SCHEMA = """
Table: case_contexts
Columns:
  - id: UUID (primary key)
  - title: VARCHAR — short issue title
  - description: TEXT — full issue description
  - raw_context: JSONB — structured diagnostic payload:
      {
        "inputs":  { "device_id": str, "port": str, "issue": str, "reported_by": str, "affected_onus": int },
        "actions": [ list of steps taken ],
        "results": { key-value diagnostic measurements },
        "outcome": "open" | "resolved" | "unresolved" | "escalated"
      }
  - created_at: TIMESTAMPTZ

PostgreSQL JSONB query syntax:
  - raw_context->>'outcome'                         (text value at top level)
  - raw_context->'inputs'->>'device_id'             (nested text value)
  - (raw_context->'inputs'->>'affected_onus')::int  (nested value cast to int)
  - raw_context->'actions'                          (JSON array)
"""

# Tool definition given to Claude — allows it to run SELECT queries
SQL_TOOL = {
    "name": "run_sql_query",
    "description": "Execute a read-only SQL SELECT query against the diagnostics database and return the results as a list of rows.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "A valid PostgreSQL SELECT query.",
            }
        },
        "required": ["sql"],
    },
}

SYSTEM_PROMPT = f"""You are a network diagnostics assistant for a fibre/telecoms operator.
Answer the engineer's question by querying the diagnostics database using the run_sql_query tool.
Only use SELECT statements. Do not modify data.

{DB_SCHEMA}"""


async def _execute_sql(sql: str) -> list[dict]:
    # Reject anything that is not a SELECT to prevent writes
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    async with AsyncSessionLocal() as session:
        result = await session.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return rows


async def answer_query(question: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    messages = [{"role": "user", "content": question}]

    # Agentic loop — Claude may call the tool multiple times to refine its answer
    sql_used = None
    query_results = None

    while True:
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[SQL_TOOL],
            messages=messages,
        )

        # Claude finished and returned a plain-text answer
        if response.stop_reason == "end_turn":
            answer = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "",
            )
            return {"answer": answer, "sql": sql_used, "data": query_results}

        # Claude wants to call the SQL tool
        if response.stop_reason == "tool_use":
            tool_call = next(b for b in response.content if b.type == "tool_use")
            sql_used = tool_call.input["sql"]

            try:
                query_results = await _execute_sql(sql_used)
                tool_result_content = {"result": query_results}
            except Exception as e:
                tool_result_content = {"error": str(e)}

            # Append Claude's response and the tool result to the message history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": str(tool_result_content),
                    }
                ],
            })
            continue

        break

    return {"answer": "", "sql": sql_used, "data": query_results}
