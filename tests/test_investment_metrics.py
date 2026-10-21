import pandas as pd
import pytest

from app.calculations.investment_metrics import (
    calculate_annualized_return,
    calculate_average_return,
    calculate_investment_score,
    calculate_total_return,
)


def test_calculate_total_return():
    prices = pd.Series([100, 110, 120])

    result = calculate_total_return(prices)

    assert result == pytest.approx(0.20)


def test_calculate_annualized_return():
    prices = pd.Series([100, 110, 120])

    result = calculate_annualized_return(
        prices,
        periods_per_year=2,
    )

    expected = (120 / 100) ** (2 / 2) - 1

    assert result == pytest.approx(expected)


def test_calculate_average_return():
    returns = pd.Series([0.10, -0.05, 0.08])

    result = calculate_average_return(returns)

    expected = (0.10 - 0.05 + 0.08) / 3

    assert result == pytest.approx(expected)


def test_calculate_investment_score():
    result = calculate_investment_score(
        annualized_return=0.10,
        volatility=0.20,
        sharpe_ratio=1.50,
    )

    expected = (
        0.10 * 40
        + 1.50 * 30
        - 0.20 * 30
    )

    assert result == pytest.approx(expected)


def test_empty_prices_are_rejected():
    prices = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_total_return(prices)


def test_single_price_is_rejected_for_annualized_return():
    prices = pd.Series([100])

    with pytest.raises(ValueError):
        calculate_annualized_return(prices)


def test_negative_prices_are_rejected():
    prices = pd.Series([100, -110, 120])

    with pytest.raises(ValueError):
        calculate_total_return(prices)


def test_empty_returns_are_rejected():
    returns = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_average_return(returns)


def test_negative_volatility_is_rejected():
    with pytest.raises(ValueError):
        calculate_investment_score(
            annualized_return=0.10,
            volatility=-0.20,
            sharpe_ratio=1.50,
        )