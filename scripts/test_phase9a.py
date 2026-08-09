import os
import sys

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.agent_factory import AgentFactory
from src.tools.registry import ToolRegistry
from src.agents.planner import KeywordPlanner
from src.agents.memory import AgentMemory
from src.agents.workflow import WorkflowEngine
from src.agents.schemas import ExecutionPlan
import src.tools.implementations  # Ensure tools are registered

def test_tool_registration():
    print("Testing Tool Registration...")
    tools = ToolRegistry.list_tools()
    assert "CalculatorTool" in tools
    assert "DateTimeTool" in tools
    assert "KnowledgeBaseTool" in tools
    assert "HealthCheckTool" in tools
    print("Tool Registration OK.\n")

def test_planner_routing():
    print("Testing KeywordPlanner Routing...")
    planner = KeywordPlanner()
    
    # Calc
    plan_calc = planner.plan("calculate 10 + 5")
    assert plan_calc.execution_type == "tool"
    assert "CalculatorTool" in plan_calc.selected_tools
    
    # Time
    plan_time = planner.plan("what is the time now?")
    assert plan_time.execution_type == "tool"
    assert "DateTimeTool" in plan_time.selected_tools
    
    # System
    plan_sys = planner.plan("check system health")
    assert plan_sys.execution_type == "mixed"
    assert "HealthCheckTool" in plan_sys.selected_tools
    
    print("KeywordPlanner Routing OK.\n")

def test_tool_execution():
    print("Testing Tool Execution...")
    calc = ToolRegistry.get_tool("CalculatorTool")
    res = calc.execute(expression="10 * 5")
    assert res.get("result") == 50
    
    dt = ToolRegistry.get_tool("DateTimeTool")
    res_dt = dt.execute()
    assert "date" in res_dt
    
    health = ToolRegistry.get_tool("HealthCheckTool")
    res_h = health.execute()
    assert res_h.get("status") == "healthy"
    print("Tool Execution OK.\n")

def test_workflow_execution():
    print("Testing Workflow Engine...")
    planner = KeywordPlanner()
    engine = WorkflowEngine()
    
    plan = planner.plan("check system health")
    result = engine.execute(plan)
    assert result.status == "success"
    assert len(result.outputs) == 2  # Health and Status tools
    print("Workflow Engine OK.\n")

def test_agent_factory():
    print("Testing Agent Factory...")
    simple = AgentFactory.create("simple")
    assert simple is not None
    
    workflow = AgentFactory.create("workflow")
    assert workflow is not None
    print("Agent Factory OK.\n")

if __name__ == "__main__":
    test_tool_registration()
    test_planner_routing()
    test_tool_execution()
    test_workflow_execution()
    test_agent_factory()
    print("ALL PHASE 9A TESTS PASSED!")
