from fastapi import APIRouter, HTTPException
from app.schemas.request_schema import ChatRequest
from app.schemas.response_schema import ChatResponse
from langchain_core.messages import HumanMessage
from app.agent.supervisor.supervisor import super_agent_workflow

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        initial_state = {"messages": [HumanMessage(content=request.message)], "next_workers": []}

        final_state = await super_agent_workflow.ainvoke(
            initial_state,
            {"recursion_limit": 10},
        )

        response_message = str(final_state["messages"][-1].content)

        return ChatResponse(
            response=response_message,
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Multi-Agent Customer Support"}