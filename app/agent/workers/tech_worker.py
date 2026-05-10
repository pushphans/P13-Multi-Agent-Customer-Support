from langchain.chat_models import init_chat_model
from typing import Annotated, TypedDict
from langchain.messages import AnyMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from app.core.config import settings
from langgraph.graph import START, END, StateGraph
from app.core.tools import tech_tools


class WorkerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


llm = init_chat_model(
    model="gpt-4o", model_provider="openai", api_key=settings.OPENAI_API_KEY
)


llm_with_tools = llm.bind_tools(tech_tools)


async def manager_node(state: WorkerState) -> WorkerState:

    messages = state["messages"]
    system_msg = SystemMessage(content="""You are a Technical Support Expert. 
    Troubleshoot app crashes, login errors, and bugs using your tools. 
    Only answer technical questions. Provide step-by-step solutions.""")

    response = await llm_with_tools.ainvoke([system_msg] + messages)
    return {"messages": [response]}


tool_node = ToolNode(tools=tech_tools)


graph = StateGraph(state_schema=WorkerState)
graph.add_node("manager_node", manager_node)
graph.add_node("tool_node", tool_node)

graph.add_edge(START, "manager_node")
graph.add_conditional_edges(
    "manager_node",
    tools_condition,
    {"tools": "tool_node", "__end__": END},
)

graph.add_edge("tool_node", "manager_node")
tech_worker = graph.compile()
