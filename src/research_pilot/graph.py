from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from research_pilot.state import State
import litellm
from dotenv import load_dotenv

load_dotenv()

# Nodes
def query(state: State, config: RunnableConfig):
    # Call DeepSeek model via LiteLLM
    response = litellm.completion(
        model="deepseek/deepseek-chat",  # Use appropriate DeepSeek model name
        messages=[{"role": "user", "content": state.content}],
        temperature=0.7,
    )
    
    # Update state with the answer
    state.content = response.choices[0].message.content
    
    return state

# Add nodes and edges
builder = StateGraph(State, input=State, output=State)
builder.add_node("query", query)

# Add edges
builder.add_edge(START, "query")
builder.add_edge("query", END)

graph = builder.compile()
