from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from regguard.core.config import settings

@tool
def calculator(expression: str) -> str:
    """ Perform basic arithmetic calculations """
    result = eval(expression)
    return str(result)

def create_calculator_agent():
   
    llm = ChatAnthropic(
       model='claude-sonnet-4-5-20250929',
       api_key=settings.ANTHROPIC_API_KEY
    )

    agent = create_agent(
       model=llm,
       tools=[calculator],
       system_prompt="You're a helpful assistant that can perform basic arithmetic calculations.",
    )

    return agent

if __name__ == "__main__":
    agent = create_calculator_agent()

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "What is 25 multiplied by 4?"}
        ]
    })
    print(result['messages'][-1].content)