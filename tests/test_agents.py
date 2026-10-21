import pandas as pd

from app.agents.investment_agent import InvestmentAgent
from app.agents.portfolio_agent import PortfolioAgent
from app.agents.risk_agent import RiskAgent
from app.models.schemas import AgentStatus


# ============================================================
# Helper: Create Market Data
# ============================================================

def create_market_data(symbol="TCS"):
    """
    Create deterministic historical market data for testing.
    """

    return pd.DataFrame(
        {
            "date": pd.date_range(
                start="2025-01-01",
                periods=5,
                freq="D",
            ),
            "symbol": [
                symbol,
                symbol,
                symbol,
                symbol,
                symbol,
            ],
            "close": [
                100.0,
                102.0,
                101.0,
                104.0,
                103.0,
            ],
        }
    )


# ============================================================
# Dummy Local Provider
# ============================================================

class DummyLocalProvider:
    """
    Mimics the local_provider component used by
    RiskAgent's FallbackDataProvider.
    """

    def get_market_data(self, local_file_path):
        """
        Return deterministic local market data.

        The actual file does not need to exist because this is
        a unit-test double.
        """

        return create_market_data("TCS")


# ============================================================
# Dummy Data Provider
# ============================================================

class DummyDataProvider:
    """
    Mimics the structure required by the agents.

    RiskAgent accesses:
        data_provider.local_provider.get_market_data(...)

    InvestmentAgent accesses:
        data_provider.get_market_data(...)
    """

    def __init__(self):
        self.local_provider = DummyLocalProvider()

    def get_market_data(
        self,
        symbol=None,
        local_file_path=None,
        *args,
        **kwargs,
    ):
        """
        Provide market data for InvestmentAgent.
        """

        if symbol is None:
            symbol = "TCS"

        return create_market_data(symbol)


# ============================================================
# Investment Agent - Basic
# ============================================================

def test_investment_agent():
    """
    Basic InvestmentAgent execution test.
    """

    agent = InvestmentAgent()

    result = agent.execute(
        query="Analyze investment opportunities for TCS.",
        budget=1000,
    )

    assert result.agent_name == "Investment Agent"

    assert result.status == AgentStatus.COMPLETED

    assert result.used_budget == 600


# ============================================================
# Risk Agent - Basic
# ============================================================

def test_risk_agent():
    """
    Basic RiskAgent execution test.
    """

    agent = RiskAgent()

    result = agent.execute(
        query="Analyze investment risk for TCS.",
        budget=1000,
    )

    assert result.agent_name == "Risk Agent"

    assert result.status == AgentStatus.COMPLETED

    assert result.used_budget == 400


# ============================================================
# Portfolio Agent - Basic
# ============================================================

def test_portfolio_agent():
    """
    Basic PortfolioAgent execution test.
    """

    agent = PortfolioAgent()

    result = agent.execute(
        query="Build a portfolio using TCS and INFY.",
        budget=1000,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.status == AgentStatus.COMPLETED

    assert result.used_budget == 500


# ============================================================
# Risk Agent - Real Market Analysis
# ============================================================

def test_risk_agent_real_market_analysis():
    """
    Test RiskAgent using explicit historical market data.
    """

    market_data = create_market_data("TCS")

    agent = RiskAgent()

    result = agent.execute(
        query="Analyze risk for TCS.",
        budget=1000,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED

    assert result.agent_name == "Risk Agent"

    assert result.output is not None

    assert "TCS" in result.output

    assert "volatility" in result.output.lower()

    assert "drawdown" in result.output.lower()

    assert "sharpe" in result.output.lower()


# ============================================================
# Risk Agent - Unsupported Symbol
# ============================================================

def test_risk_agent_fails_without_supported_symbol():
    """
    RiskAgent should fail when the requested symbol is not
    available in the supplied market data.
    """

    market_data = create_market_data("TCS")

    agent = RiskAgent()

    result = agent.execute(
        query="Analyze AAPL risk.",
        budget=1000,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED

    assert (
        result.failure_reason
        == "No supported symbol found in query."
    )


# ============================================================
# Risk Agent - Data Provider
# ============================================================

def test_risk_agent_uses_data_provider():
    """
    Test that RiskAgent obtains market data through the
    configured fallback data provider.
    """

    provider = DummyDataProvider()

    agent = RiskAgent(
        data_provider=provider,
        local_file_path="dummy_market_data.csv",
    )

    result = agent.execute(
        query="Analyze risk for TCS.",
        budget=1000,
    )

    assert result.status == AgentStatus.COMPLETED

    assert result.agent_name == "Risk Agent"

    assert result.output is not None

    assert "TCS" in result.output


# ============================================================
# Investment Agent - Real Market Analysis
# ============================================================

def test_investment_agent_real_market_analysis():
    """
    Test InvestmentAgent using explicit historical market data.
    """

    market_data = create_market_data("TCS")

    agent = InvestmentAgent()

    result = agent.execute(
        query="Analyze investment opportunities for TCS.",
        budget=1000,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED

    assert result.agent_name == "Investment Agent"

    assert result.output is not None

    assert "TCS" in result.output


# ============================================================
# Investment Agent - Unsupported Symbol
# ============================================================

def test_investment_agent_fails_without_supported_symbol():
    """
    InvestmentAgent should fail when the requested symbol is
    not available in the supplied market data.
    """

    market_data = create_market_data("TCS")

    agent = InvestmentAgent()

    result = agent.execute(
        query="Analyze investment opportunities for AAPL.",
        budget=1000,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED

    assert (
        result.failure_reason
        == "No market data available for AAPL."
    )


# ============================================================
# Investment Agent - Data Provider
# ============================================================

def test_investment_agent_uses_data_provider():
    """
    Test that InvestmentAgent obtains market data through
    its configured data provider.
    """

    provider = DummyDataProvider()

    agent = InvestmentAgent(
        data_provider=provider,
        local_file_path="dummy_market_data.csv",
    )

    result = agent.execute(
        query="Analyze investment opportunities for TCS.",
        budget=1000,
    )

    assert result.status == AgentStatus.COMPLETED

    assert result.agent_name == "Investment Agent"

    assert result.output is not None

    assert "TCS" in result.output