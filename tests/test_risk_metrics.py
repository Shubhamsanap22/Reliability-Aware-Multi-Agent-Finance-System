import pandas as pd
import pytest

from app.calculations.risk_metrics import (
    calculate_max_drawdown,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_volatility,
)


def test_calculate_returns():

    prices = pd.Series(
        [100.0, 110.0, 105.0]
    )

    returns = calculate_returns(
        prices
    )

    assert len(returns) == 2

    assert returns.iloc[0] == pytest.approx(
        0.10
    )

    assert returns.iloc[1] == pytest.approx(
        -0.0454545,
        rel=1e-5,
    )


def test_calculate_volatility():

    returns = pd.Series(
        [0.01, -0.01, 0.02, -0.02]
    )

    volatility = calculate_volatility(
        returns,
        periods_per_year=252,
    )

    assert volatility > 0


def test_calculate_max_drawdown():

    prices = pd.Series(
        [100.0, 120.0, 110.0, 90.0]
    )

    drawdown = calculate_max_drawdown(
        prices
    )

    assert drawdown == pytest.approx(
        -0.25
    )


def test_calculate_sharpe_ratio():

    returns = pd.Series(
        [0.01, 0.02, 0.015, 0.025]
    )

    sharpe = calculate_sharpe_ratio(
        returns,
        risk_free_rate=0.0,
        periods_per_year=252,
    )

    assert sharpe > 0


def test_empty_prices_are_rejected():

    prices = pd.Series(
        dtype=float
    )

    with pytest.raises(ValueError):
        calculate_returns(prices)


def test_negative_prices_are_rejected():

    prices = pd.Series(
        [100.0, -50.0, 110.0]
    )

    with pytest.raises(ValueError):
        calculate_returns(prices)