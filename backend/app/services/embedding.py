import anthropic
from app.core.config import settings

# NOTE: Anthropic does not yet expose a dedicated embeddings endpoint.
# This uses the messages API with claude-sonnet-4-5 as a placeholder.
# Replace with the real embedding model/endpoint once available.


async def get_embedding(text: str) -> list[float]:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    message = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1,
        messages=[{"role": "user", "content": text}],
    )

    # Placeholder: return a zero vector until a real embedding endpoint is used.
    _ = message
    return [0.0] * 1536
