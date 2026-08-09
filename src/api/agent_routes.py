from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from src.agents.agent_factory import AgentFactory
from src.tools.registry import ToolRegistry
from src.agents.memory import AgentMemory
import time
from src.analytics.agent_analytics import AgentAnalytics

router = APIRouter(prefix="/agent", tags=["Agent"])

class AgentRequest(BaseModel):
    query: str
    agent_type: str = "simple"

class WorkflowRequest(BaseModel):
    query: str

@router.post("/chat")
def agent_chat(request: AgentRequest):
    start = time.time()
    try:
        agent = AgentFactory.create(request.agent_type)
        response = agent.run(request.query)
        duration = time.time() - start
        AgentAnalytics.record_execution(duration)
        return {"response": response, "agent_type": request.agent_type, "latency": duration}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run")
def agent_run(request: WorkflowRequest):
    # Explicitly runs the workflow agent
    start = time.time()
    try:
        agent = AgentFactory.create("workflow")
        response = agent.run(request.query)
        duration = time.time() - start
        AgentAnalytics.record_execution(duration)
        return {"response": response, "latency": duration}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
def get_tools():
    tools = ToolRegistry.list_tools()
    details = []
    for t in tools:
        meta = ToolRegistry.get_tool(t).metadata
        details.append({
            "name": meta.name,
            "description": meta.description
        })
    return {"tools": details}

@router.get("/history")
def get_history():
    history = AgentMemory.list_all()
    return {"history": [h.dict() for h in history]}

@router.post("/workflow")
def execute_custom_workflow(request: WorkflowRequest):
    return agent_run(request)
