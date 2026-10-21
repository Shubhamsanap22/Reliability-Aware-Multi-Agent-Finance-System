from typing import Literal


RiskLevel = Literal[
    "Low",
    "Moderate",
    "High",
]


def classify_risk(
    volatility: float,
    max_drawdown: float,
) -> RiskLevel:
    """
    Classify investment risk using historical
    volatility and maximum drawdown.

    The thresholds are simplified thresholds
    intended for this project and are not a
    substitute for professional financial advice.
    """

    volatility_percent = volatility * 100
    drawdown_percent = abs(max_drawdown) * 100

    # High risk
    if (
        volatility_percent >= 30
        or drawdown_percent >= 30
    ):
        return "High"

    # Moderate risk
    if (
        volatility_percent >= 15
        or drawdown_percent >= 15
    ):
        return "Moderate"

    # Low risk
    return "Low"