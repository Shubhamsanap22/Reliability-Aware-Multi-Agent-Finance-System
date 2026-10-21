from app.models.schemas import TaskRequirement
from app.registry.capability_registry import CapabilityRegistry
from app.team.team_builder import TeamBuilder


def test_build_risk_team():
    registry = CapabilityRegistry()
    builder = TeamBuilder(registry)

    requirement = TaskRequirement(
        query="Analyze portfolio risk.",
        required_capabilities=["risk_analysis"],
    )

    team = builder.build_team(requirement)

    assert len(team) == 1
    assert team[0].name == "Risk Agent"


def test_build_portfolio_team():
    registry = CapabilityRegistry()
    builder = TeamBuilder(registry)

    requirement = TaskRequirement(
        query="Create a diversified portfolio.",
        required_capabilities=[
            "portfolio_management",
            "investment_analysis",
        ],
    )

    team = builder.build_team(requirement)

    names = {agent.name for agent in team}

    assert "Portfolio Agent" in names
    assert "Investment Agent" in names
    assert len(team) == 2


def test_unknown_capability_is_ignored():
    registry = CapabilityRegistry()
    builder = TeamBuilder(registry)

    requirement = TaskRequirement(
        query="Unknown financial task.",
        required_capabilities=["unknown_capability"],
    )

    team = builder.build_team(requirement)

    assert team == []


def test_duplicate_agent_is_not_selected_twice():
    registry = CapabilityRegistry()
    builder = TeamBuilder(registry)

    requirement = TaskRequirement(
        query="Portfolio investment analysis.",
        required_capabilities=[
            "portfolio_management",
            "investment_analysis",
        ],
    )

    team = builder.build_team(requirement)

    names = [agent.name for agent in team]

    assert len(names) == len(set(names))


def test_build_market_research_team():
    registry = CapabilityRegistry()
    builder = TeamBuilder(registry)

    requirement = TaskRequirement(
        query="Analyze the market trend of TCS.",
        required_capabilities=["market_research"],
    )

    team = builder.build_team(requirement)

    assert len(team) == 1
    assert team[0].name == "Market Research Agent"