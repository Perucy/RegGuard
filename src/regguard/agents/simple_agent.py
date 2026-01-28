"""OFAC SDN Compliance Check Agent"""

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from regguard.core.config import settings
from regguard.tools.ofac import check_ofac


async def ofac_sdn_agent(company_name: str, fuzzy: bool = True) -> str:
    """
    Run OFAC sanctions check using an AI agent.
    
    Args:
        company_name: Name to check
        fuzzy: Enable fuzzy matching
        
    Returns:
        Agent's response with sanctions check results
    """
    # Create LLM
    llm = ChatAnthropic(
        model='claude-sonnet-4-5-20250929',
        api_key=settings.ANTHROPIC_API_KEY,
        temperature=0
    )

    # Create agent with OFAC tool
    agent = create_agent(
        model=llm,
        tools=[check_ofac],
        system_prompt="You are a compliance officer. Check if companies or people are sanctioned using the OFAC tool."
    )

    # Invoke agent asynchronously (IMPORTANT!)
    result = await agent.ainvoke({
        "messages": [{
            "role": "user", 
            "content": f"Check if '{company_name}' is on the OFAC sanctions list. Use fuzzy={fuzzy}."
        }]
    })
    
    # Extract the final response
    messages = result.get('messages', [])
    if messages:
        final_message = messages[-1]
        return final_message.content
    
    return "No response from agent"