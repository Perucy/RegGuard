""" Defines what data moves between nodes """
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from regguard.core.config import settings

class AgentState(TypedDict):
    """ State flowing through the graph """
    input: str 
    processed: str
    output: str

def input_node(state: AgentState) -> AgentState:
    """ Process the input  """
    print("✅ Input Node: Received input")

    # transform the input
    user_input = state['input']
    enhanced_input = f"Please provide a clear answer to: {user_input}"

    return {
        **state,
        "input": enhanced_input
    }

def process_node(state: AgentState) -> AgentState:
    """ Call LLM to process the input """
    print("✅ Process Node: Calling LLM")

    # Create LLM
    llm = ChatAnthropic(
        model='claude-sonnet-4-5-20250929',
        api_key=settings.ANTHROPIC_API_KEY,
        temperature=0
    )

    response = llm.invoke(state['input'])

    return {
        **state,
        "processed": response.content
    }

def format_node(state: AgentState) -> AgentState:
    """ Format the output """
    print("✅ Format Node: Formatting output")

    formatted = f"""
    ═══════════════════════════════════════
    QUESTION: {state["input"].replace("Please provide a clear answer to: ", "")}
    ═══════════════════════════════════════

    ANSWER:
    {state["processed"]}

    ═══════════════════════════════════════
        """.strip()
    
    return {
        **state,
        "output": formatted
    }

def create_state_graph():
    """ State graph to connect the nodes """
    # create graph
    graph = StateGraph(AgentState)

    # add nodes
    graph.add_node("input", input_node)
    graph.add_node("process", process_node)
    graph.add_node("format", format_node)

    # add edges (connections)
    graph.add_edge(START, "input")
    graph.add_edge("input", "process")
    graph.add_edge("process", "format")
    graph.add_edge("format", END)

    # compile 
    app = graph.compile()

    return app


if __name__ == "__main__":
    app = create_state_graph()

    result = app.invoke({
        "input": "What is compliance?",
        "processed": "",
        "output": ""
    })

    print("\n" + result['output'])

    # print(app.get_graph().print_ascii()) visualize graph structure
