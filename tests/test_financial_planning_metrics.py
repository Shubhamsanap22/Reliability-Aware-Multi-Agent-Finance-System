import pytest

from app.calculations.financial_planning_metrics import (
    calculate_annual_investment,
    calculate_future_value,
    calculate_planning_score,
    calculate_required_annual_return,
    calculate_risk_adjusted_return,
    classify_planning_suitability,
)


def test_calculate_future_value():
    result = calculate_future_value(
        initial_amount=100000,
        annual_return=0.10,
        years=2,
    )

    assert result == pytest.approx(121000)


def test_future_value_rejects_invalid_amount():
    with pytest.raises(ValueError):
        calculate_future_value(
            initial_amount=0,
            annual_return=0.10,
            years=2,
        )


def test_future_value_rejects_invalid_years():
    with pytest.raises(ValueError):
        calculate_future_value(
            initial_amount=100000,
            annual_return=0.10,
            years=0,
        )


def test_calculate_required_annual_return():
    result = calculate_required_annual_return(
        initial_amount=100000,
        target_amount=121000,
        years=2,
    )

    assert result == pytest.approx(0.10)


def test_required_return_rejects_invalid_amount():
    with pytest.raises(ValueError):
        calculate_required_annual_return(
            initial_amount=0,
            target_amount=121000,
            years=2,
        )


def test_required_return_rejects_invalid_target():
    with pytest.raises(ValueError):
        calculate_required_annual_return(
            initial_amount=100000,
            target_amount=0,
            years=2,
        )


def test_calculate_annual_investment():
    result = calculate_annual_investment(
        target_amount=121000,
        annual_return=0.10,
        years=2,
    )

    assert result == pytest.approx(
        57619.0476,
        rel=1e-4,
    )


def test_annual_investment_zero_return():
    result = calculate_annual_investment(
        target_amount=100000,
        annual_return=0,
        years=5,
    )

    assert result == pytest.approx(20000)


def test_annual_investment_rejects_invalid_target():
    with pytest.raises(ValueError):
        calculate_annual_investment(
            target_amount=0,
            annual_return=0.10,
            years=5,
        )


def test_annual_investment_rejects_invalid_years():
    with pytest.raises(ValueError):
        calculate_annual_investment(
            target_amount=100000,
            annual_return=0.10,
            years=0,
        )


def test_calculate_low_risk_adjusted_return():
    result = calculate_risk_adjusted_return(
        expected_return=0.10,
        risk_level="low",
    )

    assert result == pytest.approx(0.08)


def test_calculate_moderate_risk_adjusted_return():
    result = calculate_risk_adjusted_return(
        expected_return=0.10,
        risk_level="moderate",
    )

    assert result == pytest.approx(0.06)


def test_calculate_high_risk_adjusted_return():
    result = calculate_risk_adjusted_return(
        expected_return=0.10,
        risk_level="high",
    )

    assert result == pytest.approx(0.04)


def test_risk_adjusted_return_rejects_invalid_risk():
    with pytest.raises(ValueError):
        calculate_risk_adjusted_return(
            expected_return=0.10,
            risk_level="unknown",
        )


def test_calculate_planning_score():
    result = calculate_planning_score(
        expected_return=0.10,
        risk_level="low",
        time_horizon=10,
    )

    assert result == pytest.approx(20)


def test_planning_score_moderate_risk():
    result = calculate_planning_score(
        expected_return=0.15,
        risk_level="moderate",
        time_horizon=10,
    )

    assert result == pytest.approx(10)


def test_planning_score_high_risk():
    result = calculate_planning_score(
        expected_return=0.20,
        risk_level="high",
        time_horizon=15,
    )

    assert result == pytest.approx(5)


def test_planning_score_rejects_invalid_risk():
    with pytest.raises(ValueError):
        calculate_planning_score(
            expected_return=0.10,
            risk_level="unknown",
            time_horizon=10,
        )


def test_planning_score_rejects_invalid_horizon():
    with pytest.raises(ValueError):
        calculate_planning_score(
            expected_return=0.10,
            risk_level="low",
            time_horizon=0,
        )


def test_classify_highly_suitable_plan():
    assert classify_planning_suitability(
        50
    ) == "Highly Suitable"


def test_classify_moderately_suitable_plan():
    assert classify_planning_suitability(
        30
    ) == "Moderately Suitable"


def test_classify_plan_requires_review():
    assert classify_planning_suitability(
        10
    ) == "Requires Review"