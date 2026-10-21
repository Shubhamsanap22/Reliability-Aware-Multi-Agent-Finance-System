import math

import pandas as pd


def calculate_total_return(prices: pd.Series) -> float:
    """Calculate total return over the available price history."""

    if prices.empty:
        raise ValueError("Price data cannot be empty.")

    if (prices <= 0).any():
        raise ValueError("Prices must be greater than zero.")

    return float((prices.iloc[-1] / prices.iloc[0]) - 1)


def calculate_annualized_return(
    prices: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized return from price history."""

    if prices.empty:
        raise ValueError("Price data cannot be empty.")

    if len(prices) < 2:
        raise ValueError(
            "At least two prices are required."
        )

    if (prices <= 0).any():
        raise ValueError("Prices must be greater than zero.")

    if periods_per_year <= 0:
        raise ValueError(
            "Periods per year must be greater than zero."
        )

    total_return = calculate_total_return(prices)

    periods = len(prices) - 1

    return float(
        (1 + total_return)
        ** (periods_per_year / periods)
        - 1
    )


def calculate_average_return(
    returns: pd.Series,
) -> float:
    """Calculate the arithmetic average of periodic returns."""

    if returns.empty:
        raise ValueError("Returns cannot be empty.")

    return float(returns.mean())


def calculate_investment_score(
    annualized_return: float,
    volatility: float,
    sharpe_ratio: float,
) -> float:
    """
    Calculate a simple investment score.

    The score combines return, risk, and risk-adjusted performance.
    """

    if volatility < 0:
        raise ValueError(
            "Volatility cannot be negative."
        )

    score = (
        annualized_return * 40
        + sharpe_ratio * 30
        - volatility * 30
    )

    return float(score)