from app.models.schemas import (
    AgentState,
    AgentStatus,
    BudgetState,
    TaskRequirement,
)


def test_task_requirement():

    task = TaskRequirement(
        query="Suggest an investment strategy",
        required_capabilities=[
            "investment",
            "risk_analysis",
        ],
        risk_preference="moderate",
    )

    assert task.query == "Suggest an investment strategy"
    assert "investment" in task.required_capabilities
    assert task.risk_preference == "moderate"


def test_agent_state():

    agent = AgentState(
        agent_name="Risk Agent",
        reliability=0.91,
        allocated_budget=900,
        used_budget=400,
        status=AgentStatus.FAILED,
        failure_reason="Simulated failure",
    )

    assert agent.agent_name == "Risk Agent"
    assert agent.reliability == 0.91
    assert agent.used_budget == 400
    assert agent.remaining_agent_budget == 500
    assert agent.status == AgentStatus.FAILED


def test_budget_state():

    budget = BudgetState(
        global_budget=3000,
        allocated_budget=2700,
        used_budget=1300,
        reserved_budget=300,
    )

    assert budget.remaining_budget == 1700
    assert budget.available_budget == 1400