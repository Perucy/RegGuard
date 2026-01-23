""" Service for LLM interactions """
import anthropic
from regguard.core.config import settings

async def get_chat_response(message: str) -> str:
    """ Get response from LLM

    Args:
        message (str): User message
    
    Returns:
        LLM response
    """
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    response = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": message
            }
        ]
    )
    return response.content[0].text
