import math

import pandas as pd


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate percentage returns from closing prices."""

    if prices.empty:
        raise ValueError(
            "Price series cannot be empty."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    return prices.pct_change().dropna()


def calculate_volatility(returns: pd.Series,periods_per_year: int = 252) -> float:
    """Calculate annualized volatility."""

    if returns.empty:
        raise ValueError(
            "Returns cannot be empty."
        )

    if periods_per_year <= 0:
        raise ValueError(
            "Periods per year must be greater than zero."
        )

    return float(
        returns.std()
        * math.sqrt(periods_per_year)
    )


def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calculate maximum drawdown."""

    if prices.empty:
        raise ValueError(
            "Price series cannot be empty."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    running_peak = prices.cummax()

    drawdowns = (
        prices - running_peak
    ) / running_peak

    return float(drawdowns.min())


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252) -> float:
    """Calculate annualized Sharpe ratio."""

    if returns.empty:
        raise ValueError(
            "Returns cannot be empty."
        )

    if periods_per_year <= 0:
        raise ValueError(
            "Periods per year must be greater than zero."
        )

    annualized_return = (
        returns.mean()
        * periods_per_year
    )

    annualized_volatility = (
        returns.std()
        * math.sqrt(periods_per_year)
    )

    if annualized_volatility == 0:
        raise ValueError(
            "Cannot calculate Sharpe ratio "
            "with zero volatility."
        )

    return float(
        (
            annualized_return
            - risk_free_rate
        )
        / annualized_volatility
    )