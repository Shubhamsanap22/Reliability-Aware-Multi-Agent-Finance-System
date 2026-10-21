import math


def _finite(value: float, label: str) -> float:
    """Convert a value to float and reject non-finite numbers."""

    value = float(value)

    if not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number.")

    return value


def calculate_future_value(
    initial_amount: float,
    annual_return: float,
    years: int,
) -> float:
    """Calculate the future value of a lump-sum investment."""

    initial_amount = _finite(initial_amount, "Initial amount")
    annual_return = _finite(annual_return, "Annual return")

    if initial_amount <= 0:
        raise ValueError(
            "Initial amount must be greater than zero."
        )

    if years <= 0:
        raise ValueError(
            "Investment period must be greater than zero."
        )

    if annual_return <= -1:
        raise ValueError(
            "Annual return must be greater than -100%."
        )

    return float(
        initial_amount * (1 + annual_return) ** years
    )


def calculate_required_annual_return(
    initial_amount: float,
    target_amount: float,
    years: int,
) -> float:
    """Calculate the annual compound return required for a lump sum."""

    initial_amount = _finite(initial_amount, "Initial amount")
    target_amount = _finite(target_amount, "Target amount")

    if initial_amount <= 0:
        raise ValueError(
            "Initial amount must be greater than zero."
        )

    if target_amount <= 0:
        raise ValueError(
            "Target amount must be greater than zero."
        )

    if years <= 0:
        raise ValueError(
            "Investment period must be greater than zero."
        )

    return float(
        (target_amount / initial_amount) ** (1 / years) - 1
    )


def calculate_annual_investment(
    target_amount: float,
    annual_return: float,
    years: int,
    initial_amount: float = 0.0,
) -> float:
    """
    Calculate the annual end-of-year contribution required to reach a target.

    The future value of the initial investment is subtracted from
    the target before calculating recurring contributions.
    """

    target_amount = _finite(target_amount, "Target amount")
    annual_return = _finite(annual_return, "Annual return")
    initial_amount = _finite(initial_amount, "Initial amount")

    if target_amount <= 0:
        raise ValueError(
            "Target amount must be greater than zero."
        )

    if initial_amount < 0:
        raise ValueError(
            "Initial amount cannot be negative."
        )

    if years <= 0:
        raise ValueError(
            "Investment period must be greater than zero."
        )

    if annual_return <= -1:
        raise ValueError(
            "Annual return must be greater than -100%."
        )

    initial_future_value = (
        calculate_future_value(
            initial_amount,
            annual_return,
            years,
        )
        if initial_amount > 0
        else 0.0
    )

    remaining_target = target_amount - initial_future_value

    if remaining_target <= 0:
        return 0.0

    if math.isclose(annual_return, 0.0, abs_tol=1e-12):
        return float(remaining_target / years)

    annuity_factor = (
        (1 + annual_return) ** years - 1
    ) / annual_return

    if (
        annuity_factor <= 0
        or not math.isfinite(annuity_factor)
    ):
        raise ValueError(
            "Unable to calculate a valid annual contribution "
            "for these inputs."
        )

    return float(remaining_target / annuity_factor)


def calculate_risk_adjusted_return(
    expected_return: float,
    risk_level: str,
) -> float:
    """
    Apply a transparent, project-specific risk adjustment.

    This is a heuristic, not a standard financial metric.
    """

    expected_return = _finite(
        expected_return,
        "Expected return",
    )

    normalized = risk_level.strip().lower()

    if normalized == "medium":
        normalized = "moderate"

    adjustments = {
        "low": 0.02,
        "moderate": 0.04,
        "high": 0.06,
    }

    if normalized not in adjustments:
        raise ValueError(
            "Risk level must be low, moderate/medium, or high."
        )

    return float(
        expected_return - adjustments[normalized]
    )


def calculate_planning_score(
    expected_return: float,
    risk_level: str,
    time_horizon: int,
) -> float:
    """Calculate the project-defined heuristic planning score."""

    expected_return = _finite(
        expected_return,
        "Expected return",
    )

    if time_horizon <= 0:
        raise ValueError(
            "Time horizon must be greater than zero."
        )

    normalized = risk_level.strip().lower()

    if normalized == "medium":
        normalized = "moderate"

    penalties = {
        "low": 0,
        "moderate": 15,
        "high": 30,
    }

    if normalized not in penalties:
        raise ValueError(
            "Risk level must be low, moderate/medium, or high."
        )

    score = (
        expected_return * 100
        + min(time_horizon, 20)
        - penalties[normalized]
    )

    return float(score)


def classify_planning_suitability(score: float) -> str:
    """Map the project-defined score to a descriptive category."""

    score = _finite(score, "Planning score")

    if score >= 40:
        return "Highly Suitable"

    if score >= 20:
        return "Moderately Suitable"

    return "Requires Review"