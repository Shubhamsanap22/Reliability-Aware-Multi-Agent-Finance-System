import pandas as pd
import pytest

from app.agents.portfolio_agent import PortfolioAgent
from app.models.schemas import AgentStatus


def create_market_data():
    """Create sample historical data for portfolio tests."""

    return pd.DataFrame({
        "date": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-05",
            "2026-01-06",
            "2026-01-07",
        ] * 3,
        "symbol": (
            ["TCS"] * 5
            + ["INFY"] * 5
            + ["RELIANCE"] * 5
        ),
        "open": (
            [3500, 3520, 3550, 3570, 3560]
            + [1800, 1810, 1820, 1815, 1830]
            + [1400, 1410, 1420, 1415, 1430]
        ),
        "high": (
            [3540, 3560, 3580, 3600, 3590]
            + [1830, 1840, 1850, 1845, 1860]
            + [1430, 1440, 1450, 1445, 1460]
        ),
        "low": (
            [3480, 3500, 3520, 3540, 3530]
            + [1780, 1790, 1800, 1795, 1810]
            + [1370, 1380, 1390, 1385, 1400]
        ),
        "close": (
            [3520, 3550, 3570, 3560, 3580]
            + [1810, 1820, 1815, 1830, 1840]
            + [1410, 1420, 1415, 1430, 1440]
        ),
        "volume": (
            [120000, 125000, 130000, 118000, 135000]
            + [100000, 105000, 110000, 108000, 115000]
            + [90000, 95000, 98000, 92000, 100000]
        ),
    })


def test_portfolio_agent_basic_execution():

    agent = PortfolioAgent()

    result = agent.execute(
        query="Create a diversified portfolio.",
        budget=900,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.used_budget == 500

    assert result.status == AgentStatus.COMPLETED

    assert result.output == (
        "Dummy portfolio analysis completed."
    )


def test_portfolio_agent_real_market_analysis():

    agent = PortfolioAgent()

    market_data = create_market_data()

    market_data["date"] = pd.to_datetime(
        market_data["date"]
    )

    result = agent.execute(
        query="Create a portfolio with TCS INFY RELIANCE.",
        budget=900,
        market_data=market_data,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.status == AgentStatus.COMPLETED

    assert result.used_budget == 500

    assert result.output is not None

    assert "Portfolio Assessment" in result.output

    assert "TCS" in result.output

    assert "INFY" in result.output

    assert "RELIANCE" in result.output

    assert "Portfolio return" in result.output

    assert "Portfolio volatility" in result.output

    assert "Portfolio Sharpe ratio" in result.output

    assert "Concentration (HHI)" in result.output

    assert "Diversification level" in result.output


def test_portfolio_agent_uses_equal_weights():

    agent = PortfolioAgent()

    market_data = create_market_data()

    market_data["date"] = pd.to_datetime(
        market_data["date"]
    )

    result = agent.execute(
        query="Create a portfolio with TCS INFY RELIANCE.",
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED

    assert "TCS: 33.33%" in result.output

    assert "INFY: 33.33%" in result.output

    assert "RELIANCE: 33.33%" in result.output


def test_portfolio_agent_accepts_explicit_weights():

    agent = PortfolioAgent()

    market_data = create_market_data()

    market_data["date"] = pd.to_datetime(
        market_data["date"]
    )

    result = agent.execute(
        query=(
            "Create a portfolio with "
            "TCS 50%, INFY 30%, RELIANCE 20%."
        ),
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.COMPLETED

    assert "TCS: 50.00%" in result.output

    assert "INFY: 30.00%" in result.output

    assert "RELIANCE: 20.00%" in result.output


def test_portfolio_agent_rejects_incomplete_weights():

    agent = PortfolioAgent()

    market_data = create_market_data()

    market_data["date"] = pd.to_datetime(
        market_data["date"]
    )

    result = agent.execute(
        query=(
            "Create a portfolio with "
            "TCS 60%, INFY 40%, RELIANCE."
        ),
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED

    assert result.used_budget == 0

    assert (
        result.failure_reason
        == "Weights must be provided for all selected assets."
    )


def test_portfolio_agent_fails_without_supported_symbols():

    agent = PortfolioAgent()

    market_data = create_market_data()

    market_data["date"] = pd.to_datetime(
        market_data["date"]
    )

    result = agent.execute(
        query="Create a portfolio with AAPL.",
        budget=900,
        market_data=market_data,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.status == AgentStatus.FAILED

    assert result.used_budget == 0

    assert (
        result.failure_reason
        == "No supported symbols found in query."
    )


def test_portfolio_agent_fails_with_empty_data():

    agent = PortfolioAgent()

    market_data = pd.DataFrame()

    result = agent.execute(
        query="Create a portfolio with TCS INFY.",
        budget=900,
        market_data=market_data,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.status == AgentStatus.FAILED

    assert result.used_budget == 0

    assert (
        result.failure_reason
        == "Market data is empty."
    )


def test_portfolio_agent_fails_with_insufficient_budget():

    agent = PortfolioAgent()

    result = agent.execute(
        query="Create a portfolio with TCS INFY.",
        budget=300,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.status == AgentStatus.FAILED

    assert result.used_budget == 0

    assert (
        result.failure_reason
        == "Insufficient budget."
    )


def test_portfolio_agent_uses_data_provider(
    tmp_path,
):

    from app.data.api_provider import APIDataProvider
    from app.data.data_loader import DataLoader
    from app.data.data_provider import LocalDataProvider
    from app.data.fallback_provider import (
        FallbackDataProvider,
    )

    data = create_market_data()

    file_path = tmp_path / "market_data.csv"

    data.to_csv(
        file_path,
        index=False,
    )

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader
    )

    api_provider = APIDataProvider.__new__(
        APIDataProvider
    )

    fallback_provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    agent = PortfolioAgent(
        data_provider=fallback_provider,
        local_file_path=str(file_path),
    )

    result = agent.execute(
        query="Create a portfolio with TCS INFY RELIANCE.",
        budget=900,
    )

    assert result.agent_name == "Portfolio Agent"

    assert result.status == AgentStatus.COMPLETED

    assert result.used_budget == 500

    assert result.output is not None

    assert "Portfolio Assessment" in result.output

    assert "TCS" in result.output

    assert "INFY" in result.output

    assert "RELIANCE" in result.output

    assert "Portfolio return" in result.output

    assert "Portfolio volatility" in result.output

    assert "Portfolio Sharpe ratio" in result.output


def test_portfolio_agent_rejects_invalid_weight_sum():

    agent = PortfolioAgent()

    market_data = create_market_data()

    market_data["date"] = pd.to_datetime(
        market_data["date"]
    )

    result = agent.execute(
        query=(
            "Create a portfolio with "
            "TCS 50%, INFY 20%, RELIANCE 20%."
        ),
        budget=900,
        market_data=market_data,
    )

    assert result.status == AgentStatus.FAILED

    assert result.used_budget == 0

    assert (
        result.failure_reason
        == "Portfolio weights must sum to 1."
    )