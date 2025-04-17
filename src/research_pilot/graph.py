from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from research_pilot.state import State

# Nodes
def query(state: State, config: RunnableConfig):
    return state

# Add nodes and edges
builder = StateGraph(State, input=State, output=State)
builder.add_node("query", query)

# Add edges
builder.add_edge(START, "query")
builder.add_edge("query", END)

graph = builder.compile()
