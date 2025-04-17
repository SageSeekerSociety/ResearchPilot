from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from research_pilot.state import State
import litellm
from dotenv import load_dotenv

load_dotenv()

# Nodes
def query(state: State, config: RunnableConfig):
    # If messages is empty, initialize with user content
    if not state.messages:
        state.messages.append({"role": "user", "content": state.content})

    # Call DeepSeek model via LiteLLM
    response = litellm.completion(
        model="deepseek/deepseek-chat",  # Use appropriate DeepSeek model name
        messages=state.messages,
        temperature=0.7,
    )
    
    # Get the assistant's response
    assistant_message = response.choices[0].message
    
    # Update state with the answer
    state.content = assistant_message.content
    
    # Append the assistant's response to messages
    state.messages.append({"role": "assistant", "content": assistant_message.content})
    
    return state

# Add nodes and edges
builder = StateGraph(State, input=State, output=State)
builder.add_node("query", query)

# Add edges
builder.add_edge(START, "query")
builder.add_edge("query", "query")

graph = builder.compile()
