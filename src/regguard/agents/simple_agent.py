from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from regguard.core.config import settings
from langsmith import traceable
from langsmith.wrappers import wrap_anthropic
import anthropic

client = wrap_anthropic(anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY))

@traceable(run_type="tool", name="Retrieve Context")
def my_tool(question: str) -> str:
  return "During this morning's meeting, we solved all world conflict."

@traceable(name="Chat Pipeline")
def chat_pipeline(question: str):
  context = my_tool(question)
  messages = [
      { "role": "user", "content": f"Question: {question}\nContext: {context}"}
  ]
  message = client.messages.create(
      model="claude-sonnet-4-5-20250929",
      messages=messages,
      max_tokens=1024,
      system="You are a helpful assistant. Please respond to the user's request only based on the given context."
  )
  return message

print(chat_pipeline("Can you summarize this morning's meetings?"))