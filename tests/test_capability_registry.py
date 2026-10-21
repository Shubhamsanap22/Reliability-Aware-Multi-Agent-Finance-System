from app.agents.fundamental_analysis_agent import (
    FundamentalAnalysisAgent,
)
from app.agents.investment_agent import InvestmentAgent
from app.agents.market_research_agent import MarketResearchAgent
from app.agents.portfolio_agent import PortfolioAgent
from app.agents.risk_agent import RiskAgent
from app.agents.sentiment_analysis_agent import (
    SentimentAnalysisAgent,
)
from app.agents.technical_analysis_agent import (
    TechnicalAnalysisAgent,
)
from app.registry.capability_registry import CapabilityRegistry


def test_investment_analysis_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "investment_analysis"
    )

    assert len(agents) == 2

    names = {
        agent.name
        for agent in agents
    }

    assert "Investment Agent" in names
    assert "Portfolio Agent" in names


def test_risk_analysis_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "risk_analysis"
    )

    assert len(agents) == 1

    assert isinstance(
        agents[0],
        RiskAgent,
    )


def test_portfolio_management_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "portfolio_management"
    )

    assert len(agents) == 1

    assert isinstance(
        agents[0],
        PortfolioAgent,
    )


def test_market_research_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "market_research"
    )

    assert len(agents) == 1

    assert isinstance(
        agents[0],
        MarketResearchAgent,
    )


def test_fundamental_analysis_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "fundamental_analysis"
    )

    assert len(agents) == 1

    assert isinstance(
        agents[0],
        FundamentalAnalysisAgent,
    )


def test_technical_analysis_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "technical_analysis"
    )

    assert len(agents) == 1

    assert isinstance(
        agents[0],
        TechnicalAnalysisAgent,
    )


def test_sentiment_analysis_capability():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capability(
        "sentiment_analysis"
    )

    assert len(agents) == 1

    assert isinstance(
        agents[0],
        SentimentAnalysisAgent,
    )


def test_multiple_capabilities_return_unique_agents():
    registry = CapabilityRegistry()

    agents = registry.get_agents_for_capabilities(
        [
            "investment_analysis",
            "portfolio_management",
        ]
    )

    names = [
        agent.name
        for agent in agents
    ]

    assert len(names) == len(set(names))