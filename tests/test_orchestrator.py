from app.orchestration.orchestrator import Orchestrator
from app.analysis.query_analyzer import QueryAnalyzer
from app.registry.capability_registry import CapabilityRegistry
from app.team.team_builder import TeamBuilder
from app.monitoring.reliability_monitor import ReliabilityMonitor
from app.models.schemas import AgentStatus


def test_risk_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Analyze the risk of TCS."
    )

    assert requirement.required_capabilities == [
        "risk_analysis"
    ]


def test_portfolio_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Build a portfolio using TCS and INFY."
    )

    assert requirement.required_capabilities == [
        "portfolio_management",
        "investment_analysis",
    ]


def test_investment_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Should I invest in TCS?"
    )

    assert requirement.required_capabilities == [
        "investment_analysis"
    ]


def test_market_research_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Analyze the market trend for TCS."
    )

    assert requirement.required_capabilities == [
        "market_research"
    ]


def test_market_research_team_is_selected():
    analyzer = QueryAnalyzer()
    registry = CapabilityRegistry()

    team_builder = TeamBuilder(
        registry
    )

    requirement = analyzer.analyze(
        "Analyze the market trend for TCS."
    )

    team = team_builder.build_team(
        requirement
    )

    assert len(team) == 1

    assert team[0].name == (
        "Market Research Agent"
    )


def test_fundamental_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Analyze the fundamental strength of TCS."
    )

    assert requirement.required_capabilities == [
        "fundamental_analysis"
    ]


def test_fundamental_team_is_selected():
    analyzer = QueryAnalyzer()
    registry = CapabilityRegistry()

    team_builder = TeamBuilder(
        registry
    )

    requirement = analyzer.analyze(
        "Analyze the fundamental strength of TCS."
    )

    team = team_builder.build_team(
        requirement
    )

    assert len(team) == 1

    assert team[0].name == (
        "Fundamental Analysis Agent"
    )


def test_technical_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Perform technical analysis on TCS."
    )

    assert requirement.required_capabilities == [
        "technical_analysis"
    ]


def test_technical_team_is_selected():
    analyzer = QueryAnalyzer()
    registry = CapabilityRegistry()

    team_builder = TeamBuilder(
        registry
    )

    requirement = analyzer.analyze(
        "Perform technical analysis on TCS."
    )

    team = team_builder.build_team(
        requirement
    )

    assert len(team) == 1

    assert team[0].name == (
        "Technical Analysis Agent"
    )


def test_sentiment_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "Analyze the sentiment for TCS."
    )

    assert requirement.required_capabilities == [
        "sentiment_analysis"
    ]


def test_sentiment_team_is_selected():
    analyzer = QueryAnalyzer()
    registry = CapabilityRegistry()

    team_builder = TeamBuilder(
        registry
    )

    requirement = analyzer.analyze(
        "Analyze the sentiment for TCS."
    )

    team = team_builder.build_team(
        requirement
    )

    assert len(team) == 1

    assert team[0].name == (
        "Sentiment Analysis Agent"
    )


def test_financial_planning_query_is_analyzed_correctly():
    analyzer = QueryAnalyzer()

    requirement = analyzer.analyze(
        "I want ₹20 lakh in 8 years with moderate risk"
    )

    assert requirement.required_capabilities == [
        "financial_planning"
    ]


def test_financial_planning_team_is_selected():
    analyzer = QueryAnalyzer()
    registry = CapabilityRegistry()

    team_builder = TeamBuilder(
        registry
    )

    requirement = analyzer.analyze(
        "I want ₹20 lakh in 8 years with moderate risk"
    )

    team = team_builder.build_team(
        requirement
    )

    assert len(team) == 1

    assert team[0].name == (
        "Financial Planning Agent"
    )


def test_reliability_is_updated_after_success():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "risk_analysis"
    )

    agent = agents[0]

    initial_reliability = agent.reliability

    reliability_monitor = ReliabilityMonitor()

    reliability_monitor.update(
        agent,
        AgentStatus.COMPLETED,
    )

    assert agent.reliability > initial_reliability