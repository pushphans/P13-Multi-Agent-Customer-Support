from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router as agent_router

app = FastAPI(
    title="Multi-Agent Customer Support API",
    description="API for customer support using multi-agent system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api/v1", tags=["Agent"])


@app.get("/")
async def root():
    return {"message": "Multi-Agent Customer Support API", "docs": "/docs"}
