from app.agents.investment_agent import InvestmentAgent
from app.agents.portfolio_agent import PortfolioAgent

from app.team.selection_policy import (
    MultiFactorSelectionPolicy,
)


def test_missing_quality_and_latency_are_omitted_and_weights_renormalized():

    agents = [
        InvestmentAgent(),
        PortfolioAgent(),
    ]

    scores = MultiFactorSelectionPolicy().score_group(
        agents,
        "investment_analysis",
    )

    for score in scores.values():

        assert "analytical_quality" not in score.factors

        assert "execution_speed" not in score.factors

        assert abs(
            sum(score.weights_used.values()) - 1.0
        ) < 1e-9

        assert 0 <= score.total <= 1


def test_measured_quality_and_latency_are_included_when_available():

    investment = InvestmentAgent()

    portfolio = PortfolioAgent()

    investment.analytical_quality_score = 0.8

    investment.average_execution_time_seconds = 2.0

    portfolio.analytical_quality_score = 0.9

    portfolio.average_execution_time_seconds = 4.0

    scores = MultiFactorSelectionPolicy().score_group(
        [
            investment,
            portfolio,
        ],
        "investment_analysis",
    )

    assert (
        "analytical_quality"
        in scores[investment.name].factors
    )

    assert (
        "execution_speed"
        in scores[investment.name].factors
    )

    assert (
        scores[investment.name].factors["execution_speed"]
        == 1.0
    )

    assert (
        scores[portfolio.name].factors["execution_speed"]
        == 0.5
    )