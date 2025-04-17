from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from research_pilot.state import State
import litellm
from dotenv import load_dotenv
import arxiv
import os


load_dotenv()

# Nodes
def think_keywords(state: State, config: RunnableConfig):
    prompt = """
    你现在需要帮助用户使用 Arxiv 搜索相关的论文。请根据用户的需求，生成一些关键词，
    帮助用户搜索到最相关的论文。
    只输出关键词，不要输出任何解释。
    关键词数量不要超过 3 个。
    """
    state.messages.append({"role": "system", "content": prompt})
    state.messages.append({"role": "user", "content": state.question})

    # Call DeepSeek model via LiteLLM
    response = litellm.completion(
        model="deepseek/deepseek-chat",  # Use appropriate DeepSeek model name
        messages=state.messages,
        temperature=0.7,
    )
    
    # Get the assistant's response
    assistant_message = response.choices[0].message
    
    # Update state with the answer
    state.keywords = assistant_message.content
    
    # Append the assistant's response to messages
    state.messages.append({"role": "assistant", "content": assistant_message.content})
    
    return state

def search_papers(state: State, config: RunnableConfig):
    client = arxiv.Client()
    search = arxiv.Search(query=state.keywords, max_results=30)
    state.search_results = list(client.results(search))
    return state

def select_papers(state: State, config: RunnableConfig):
    prompt = """
    你现在需要从搜索到的论文中选择一些论文，
    帮助用户搜索到最相关的论文。
    只输出论文的编号，用英文逗号分隔。不要输出任何解释。
    论文数量不要超过 3 篇。
    """
    query = "\n".join([f"{i+1}. {paper.title}" for i, paper in enumerate(state.search_results)])
    state.messages.append({"role": "system", "content": prompt})
    state.messages.append({"role": "user", "content": query})

    # Call DeepSeek model via LiteLLM
    response = litellm.completion(
        model="deepseek/deepseek-chat",  # Use appropriate DeepSeek model name
        messages=state.messages,
        temperature=0.7,
    )
    
    # Get the assistant's response
    assistant_message = response.choices[0].message
    
    # Update state with the answer
    paper_ids = [int(paper) for paper in assistant_message.content.split(",")]
    state.selected_papers = [state.search_results[i-1] for i in paper_ids]

    state.messages.append({"role": "assistant", "content": assistant_message.content})

    return state

def get_paper_contents(state: State, config: RunnableConfig):
    os.makedirs("papers", exist_ok=True)
    client = arxiv.Client()
    for paper in state.selected_papers:
        paper.download_pdf(dirpath="papers")
        print(f"Downloaded {paper.title} to papers/{paper.title}.pdf")
        state.selected_paper_contents.append(paper.title+" (content is yet to be implemented)")
    return state

# Add nodes and edges
builder = StateGraph(State, input=State, output=State)
builder.add_node("think_keywords", think_keywords)
builder.add_node("search_papers", search_papers)
builder.add_node("select_papers", select_papers)
builder.add_node("get_paper_contents", get_paper_contents)

# Add edges
builder.add_edge(START, "think_keywords")
builder.add_edge("think_keywords", "search_papers")
builder.add_edge("search_papers", "select_papers")
builder.add_edge("select_papers", "get_paper_contents")
builder.add_edge("get_paper_contents", END)

graph = builder.compile()
