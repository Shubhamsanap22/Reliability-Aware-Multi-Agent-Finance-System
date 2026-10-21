import pandas as pd


def calculate_revenue_growth(
    revenue: pd.Series,
) -> float:
    """Calculate revenue growth from first to last period."""

    if revenue.empty:
        raise ValueError(
            "Revenue data cannot be empty."
        )

    if len(revenue) < 2:
        raise ValueError(
            "At least two revenue values are required."
        )

    if (revenue <= 0).any():
        raise ValueError(
            "Revenue values must be greater than zero."
        )

    return float(
        (revenue.iloc[-1] / revenue.iloc[0]) - 1
    )


def calculate_profit_margin(
    revenue: pd.Series,
    net_income: pd.Series,
) -> float:
    """Calculate net profit margin using the latest period."""

    if revenue.empty or net_income.empty:
        raise ValueError(
            "Revenue and net income data cannot be empty."
        )

    if len(revenue) != len(net_income):
        raise ValueError(
            "Revenue and net income must have the same length."
        )

    if (revenue <= 0).any():
        raise ValueError(
            "Revenue values must be greater than zero."
        )

    latest_revenue = float(revenue.iloc[-1])
    latest_net_income = float(net_income.iloc[-1])

    return float(
        latest_net_income / latest_revenue
    )


def calculate_eps_growth(
    eps: pd.Series,
) -> float:
    """Calculate EPS growth from first to last period."""

    if eps.empty:
        raise ValueError(
            "EPS data cannot be empty."
        )

    if len(eps) < 2:
        raise ValueError(
            "At least two EPS values are required."
        )

    if (eps <= 0).any():
        raise ValueError(
            "EPS values must be greater than zero."
        )

    return float(
        (eps.iloc[-1] / eps.iloc[0]) - 1
    )


def calculate_price_to_earnings(
    price: float,
    eps: float,
) -> float:
    """Calculate the price-to-earnings ratio."""

    if price <= 0:
        raise ValueError(
            "Price must be greater than zero."
        )

    if eps <= 0:
        raise ValueError(
            "EPS must be greater than zero."
        )

    return float(price / eps)


def calculate_fundamental_score(
    revenue_growth: float,
    profit_margin: float,
    eps_growth: float,
    pe_ratio: float,
) -> float:
    """
    Calculate a project-specific fundamental score.

    Higher revenue growth, profit margin, and EPS growth
    increase the score, while a higher P/E ratio reduces it.
    """

    if pe_ratio <= 0:
        raise ValueError(
            "P/E ratio must be greater than zero."
        )

    score = (
        revenue_growth * 30
        + profit_margin * 30
        + eps_growth * 25
        - (pe_ratio / 100) * 15
    )

    return float(score)


def classify_fundamental_strength(
    fundamental_score: float,
) -> str:
    """Classify the overall fundamental strength."""

    if fundamental_score >= 20:
        return "Strong Fundamentals"

    if fundamental_score >= 8:
        return "Moderate Fundamentals"

    return "Weak Fundamentals"