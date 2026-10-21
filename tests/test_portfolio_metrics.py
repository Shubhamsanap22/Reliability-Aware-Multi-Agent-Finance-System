import pandas as pd
import pytest

from app.calculations.portfolio_metrics import (
    calculate_concentration,
    calculate_portfolio_return,
    calculate_portfolio_sharpe_ratio,
    calculate_portfolio_volatility,
    classify_diversification,
)


def test_calculate_portfolio_return():

    asset_returns = {
        "TCS": 0.10,
        "RELIANCE": 0.08,
    }

    weights = {
        "TCS": 0.60,
        "RELIANCE": 0.40,
    }

    result = calculate_portfolio_return(
        asset_returns,
        weights,
    )

    expected = (
        0.10 * 0.60
        + 0.08 * 0.40
    )

    assert result == pytest.approx(
        expected
    )


def test_calculate_portfolio_volatility():

    returns = pd.DataFrame({
        "TCS": [
            0.01,
            0.02,
            -0.01,
            0.03,
            0.01,
        ],
        "RELIANCE": [
            0.02,
            0.01,
            0.00,
            0.02,
            0.01,
        ],
    })

    weights = {
        "TCS": 0.50,
        "RELIANCE": 0.50,
    }

    result = calculate_portfolio_volatility(
        returns,
        weights,
    )

    assert result >= 0


def test_calculate_portfolio_sharpe_ratio():

    result = calculate_portfolio_sharpe_ratio(
        portfolio_return=0.12,
        portfolio_volatility=0.20,
        risk_free_rate=0.03,
    )

    expected = (
        (0.12 - 0.03)
        / 0.20
    )

    assert result == pytest.approx(
        expected
    )


def test_calculate_concentration():

    weights = {
        "TCS": 0.50,
        "RELIANCE": 0.30,
        "INFY": 0.20,
    }

    result = calculate_concentration(
        weights
    )

    expected = (
        0.50 ** 2
        + 0.30 ** 2
        + 0.20 ** 2
    )

    assert result == pytest.approx(
        expected
    )


def test_classify_well_diversified():

    result = classify_diversification(
        0.15
    )

    assert result == "Well Diversified"


def test_classify_moderately_diversified():

    result = classify_diversification(
        0.25
    )

    assert result == "Moderately Diversified"


def test_classify_highly_concentrated():

    result = classify_diversification(
        0.40
    )

    assert result == "Highly Concentrated"


def test_empty_returns_are_rejected():

    with pytest.raises(ValueError):

        calculate_portfolio_return(
            {},
            {},
        )


def test_weights_must_sum_to_one():

    with pytest.raises(ValueError):

        calculate_portfolio_return(
            {
                "TCS": 0.10,
                "RELIANCE": 0.08,
            },
            {
                "TCS": 0.50,
                "RELIANCE": 0.30,
            },
        )


def test_negative_weights_are_rejected():

    with pytest.raises(ValueError):

        calculate_concentration(
            {
                "TCS": 1.20,
                "RELIANCE": -0.20,
            }
        )


def test_zero_volatility_is_rejected():

    with pytest.raises(ValueError):

        calculate_portfolio_sharpe_ratio(
            portfolio_return=0.10,
            portfolio_volatility=0.0,
        )