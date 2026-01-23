import anthropic
from regguard.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What should I search for to find the latest trends in AI?"
        }
    ]
)
print(message)