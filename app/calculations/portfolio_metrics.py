import math
from typing import Mapping

import numpy as np
import pandas as pd


def _validate_weights(weights: Mapping[str, float]) -> None:
    """Ensure portfolio weights are valid and sum to one."""
    if not weights:
        raise ValueError("Portfolio weights cannot be empty.")

    values = [float(value) for value in weights.values()]

    if any(not math.isfinite(value) for value in values):
        raise ValueError("Portfolio weights must be finite numbers.")

    if any(value < 0 for value in values):
        raise ValueError("Portfolio weights cannot be negative.")

    if not math.isclose(
        sum(values),
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        raise ValueError("Portfolio weights must sum to 1.")


def calculate_portfolio_return(
    asset_returns: dict[str, float],
    weights: dict[str, float],
) -> float:
    """Calculate the weighted holding-period asset return."""
    if not asset_returns:
        raise ValueError("Asset returns cannot be empty.")

    if set(asset_returns) != set(weights):
        raise ValueError(
            "Asset returns and weights must contain the same assets."
        )

    _validate_weights(weights)

    if any(
        not math.isfinite(float(value))
        for value in asset_returns.values()
    ):
        raise ValueError("Asset returns must be finite numbers.")

    return float(
        sum(
            float(asset_returns[asset]) * float(weights[asset])
            for asset in asset_returns
        )
    )


def calculate_portfolio_volatility(
    returns: pd.DataFrame,
    weights: dict[str, float],
    periods_per_year: int = 252,
) -> float:
    """Calculate annualized volatility from aligned periodic returns."""
    if returns.empty:
        raise ValueError("Returns data cannot be empty.")

    if periods_per_year <= 0:
        raise ValueError("Periods per year must be greater than zero.")

    _validate_weights(weights)

    missing = [
        asset for asset in weights
        if asset not in returns.columns
    ]

    if missing:
        raise ValueError(
            f"Missing return data for assets: {missing}"
        )

    selected = returns[list(weights)].apply(
        pd.to_numeric,
        errors="coerce",
    )

    selected = selected.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna(how="any")

    if len(selected) < 2:
        raise ValueError(
            "At least two aligned return observations are required "
            "to calculate portfolio volatility."
        )

    covariance = selected.cov()

    if covariance.isna().any().any():
        raise ValueError(
            "Portfolio covariance matrix contains invalid values."
        )

    weight_vector = pd.Series(
        weights,
        dtype=float,
    ).reindex(selected.columns)

    variance = float(
        weight_vector.T @ covariance @ weight_vector
    )

    if not math.isfinite(variance) or variance < -1e-12:
        raise ValueError("Portfolio variance is invalid.")

    variance = max(variance, 0.0)

    return float(
        math.sqrt(variance) * math.sqrt(periods_per_year)
    )


def calculate_portfolio_sharpe_ratio(
    portfolio_return: float,
    portfolio_volatility: float,
    risk_free_rate: float = 0.0,
) -> float:
    """Calculate Sharpe ratio using annualized return and volatility."""
    values = (
        portfolio_return,
        portfolio_volatility,
        risk_free_rate,
    )

    if not all(math.isfinite(value) for value in values):
        raise ValueError("Sharpe ratio inputs must be finite numbers.")

    if portfolio_volatility < 0:
        raise ValueError("Portfolio volatility cannot be negative.")

    if portfolio_volatility == 0:
        raise ValueError(
            "Cannot calculate Sharpe ratio with zero volatility."
        )

    return float(
        (portfolio_return - risk_free_rate)
        / portfolio_volatility
    )


def calculate_concentration(
    weights: dict[str, float],
) -> float:
    """Calculate the Herfindahl-Hirschman concentration index."""
    _validate_weights(weights)

    return float(
        sum(float(weight) ** 2 for weight in weights.values())
    )


def classify_diversification(concentration: float) -> str:
    """Classify concentration using project-defined HHI thresholds."""
    if not math.isfinite(concentration) or not 0 <= concentration <= 1:
        raise ValueError(
            "Concentration must be finite and between 0 and 1."
        )

    if concentration < 0.20:
        return "Well Diversified"

    if concentration < 0.35:
        return "Moderately Diversified"

    return "Highly Concentrated"