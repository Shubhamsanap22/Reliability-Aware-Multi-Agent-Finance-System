from unittest.mock import MagicMock

from app.analysis.query_analyzer import QueryAnalyzer
from app.models.schemas import TaskRequirement
from app.orchestration.orchestrator import Orchestrator
from app.team.team_builder import TeamBuilder


def test_mistral_analyzer_returns_requirement():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Should I invest in TCS?"
    )

    assert isinstance(requirement, TaskRequirement)
    assert requirement.query == "Should I invest in TCS?"
    assert "investment_analysis" in requirement.required_capabilities
    assert "TCS" in requirement.symbols


def test_team_builder_selects_investment_agent():
    analyzer = MagicMock()

    analyzer.analyze.return_value = TaskRequirement(
        query="Should I invest in TCS?",
        required_capabilities=["investment_analysis"],
        symbols=["TCS"],
    )

    team_builder = TeamBuilder()

    requirement = analyzer.analyze(
        "Should I invest in TCS?"
    )

    team = team_builder.build_team(requirement)

    assert len(team) == 1
    assert team[0].__class__.__name__ == "InvestmentAgent"


def test_team_builder_selects_risk_agent():
    team_builder = TeamBuilder()

    requirement = TaskRequirement(
        query="What is the risk of investing in TCS?",
        required_capabilities=["risk_analysis"],
        symbols=["TCS"],
    )

    team = team_builder.build_team(requirement)

    assert len(team) == 1
    assert team[0].__class__.__name__ == "RiskAgent"


def test_team_builder_selects_multiple_agents():
    team_builder = TeamBuilder()

    requirement = TaskRequirement(
        query="Analyze technical indicators and risk of TCS.",
        required_capabilities=[
            "technical_analysis",
            "risk_analysis",
        ],
        symbols=["TCS"],
    )

    team = team_builder.build_team(requirement)

    assert len(team) == 2

    agent_names = {
        agent.__class__.__name__
        for agent in team
    }

    assert "TechnicalAnalysisAgent" in agent_names
    assert "RiskAgent" in agent_names