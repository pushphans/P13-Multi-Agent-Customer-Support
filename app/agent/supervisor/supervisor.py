from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from typing import List
from langchain.messages import SystemMessage

# Import kiya - yeh compiled graph hain (worker files se)
# billing_workflow = billing_worker.py se aaya hai (line 56)
# tech_worker_workflow = tech_worker.py se aaya hai (line 49)
from app.agent.workers.billing_worker import billing_worker
from app.agent.workers.tech_worker import tech_worker
from app.core.config import settings

from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.types import Send


# ---------------------------------------------------------
# STATE SCHEMA
# ---------------------------------------------------------
class AgentState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    next_workers: List[str]


# ---------------------------------------------------------
# STRUCTURED OUTPUT SCHEMA
# ---------------------------------------------------------
class SupervisorStructuredOutput(BaseModel):
    next_workers: List[str] = Field(
        description="List of workers to assign tasks to. Options: 'billing_worker', 'tech_worker', or 'FINISH'."
    )


# ---------------------------------------------------------
# BOSS SETUP
# ---------------------------------------------------------
llm = init_chat_model(
    model="gpt-4o", model_provider="openai", api_key=settings.OPENAI_API_KEY
)

# Yahan hum tools bind nahi kar rahe, hum Output ko structure kar rahe hain!
structured_boss = llm.with_structured_output(schema=SupervisorStructuredOutput)


# ---------------------------------------------------------
# SUPERVISOR NODE (The Brain)
# ---------------------------------------------------------
async def supervisor_node(state: AgentState) -> dict:
    messages = state["messages"]

    system_msg = SystemMessage(
        content="""You are a Supervisor in a tech company.
    Your workers are:
    - 'billing_worker': Handles money, refunds, transactions.
    - 'tech_worker': Handles app crashes, errors, login issues.

    RULES FOR ROUTING:
    1. INDEPENDENT TASKS: If tasks don't depend on each other, output all required workers to run parallelly.
    2. DEPENDENT TASKS: If task B needs the result of task A, ONLY output the worker for task A first. Wait for its result in the history before calling task B.
    3. EXIT STRATEGY (CRITICAL): If the user's request is fulfilled, OR if the workers cannot solve the issue because they lack the right tools, you MUST output ['FINISH']. Do not retry indefinitely!"""
    )
    # Boss thinks and directly outputs the Pydantic schema
    result = await structured_boss.ainvoke([system_msg] + messages)

    # Return dictionary that updates our global AgentState
    return {"next_workers": result.next_workers}


async def parallel_router(state: AgentState):

    next_workers = state.get("next_workers", [])

    # 1. PEHLI CONDITION (The Happy Path): Agar Boss ne bola ki kaam khatam
    if "FINISH" in next_workers:
        print("[ROUTER] Boss ne FINISH bola. Graph END kar rahe hain.")
        return END

    elif len(next_workers) == 0:
        print("[ROUTER] List khali hai! Safety ke liye Graph END kar rahe hain.")
        return END

    else:
        print(f"[ROUTER] In workers ko fire kar rahe hain: {next_workers}")
        tasks = []

        for worker_name in next_workers:
            tasks.append(Send(node=worker_name, arg={"messages": state["messages"]}))

        return tasks


# ----------------------------------------------------------
# GRAPH STRUCTURE
# ----------------------------------------------------------
graph = StateGraph(state_schema=AgentState)
graph.add_node("supervisor_node", supervisor_node)
graph.add_node("billing_worker", billing_worker)
graph.add_node("tech_worker", tech_worker)


graph.add_edge(START, "supervisor_node")
graph.add_conditional_edges(
    "supervisor_node",
    parallel_router,
    ["billing_worker", "tech_worker", END],
)
graph.add_edge("billing_worker", "supervisor_node")
graph.add_edge("tech_worker", "supervisor_node")


super_agent_workflow = graph.compile()
