from langchain.chat_models import init_chat_model
from typing import Annotated, TypedDict
from langchain.messages import AnyMessage
from langchain.messages import SystemMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from app.core.config import settings

from app.core.tools import billing_tools

llm = init_chat_model(
    model="gpt-4o", model_provider="openai", api_key=settings.OPENAI_API_KEY
)


llm_with_tools = llm.bind_tools(billing_tools)


# Worker State
class WorkerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


async def manager_node(state: WorkerState) -> WorkerState:
    messages = state["messages"]

    system_msg = SystemMessage(content="""You are a Billing Expert. 
    Solve refund and transaction issues using your tools. 
    Only answer billing related questions. Be concise.""")

    response = await llm_with_tools.ainvoke([system_msg] + messages)

    return {"messages": [response]}


tool_node = ToolNode(tools=billing_tools)


billing_worker_graph = StateGraph(state_schema=WorkerState)

billing_worker_graph.add_node("manager_node", manager_node)
billing_worker_graph.add_node("tool_node", tool_node)


billing_worker_graph.add_edge(START, "manager_node")
billing_worker_graph.add_conditional_edges(
    "manager_node",
    tools_condition,
    {"tools": "tool_node", "__end__": END},
)

billing_worker_graph.add_edge("tool_node", "manager_node")


billing_worker = billing_worker_graph.compile()
