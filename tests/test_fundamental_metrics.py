import pandas as pd
import pytest

from app.calculations.fundamental_metrics import (
    calculate_eps_growth,
    calculate_fundamental_score,
    calculate_price_to_earnings,
    calculate_profit_margin,
    calculate_revenue_growth,
    classify_fundamental_strength,
)


def test_calculate_revenue_growth():
    revenue = pd.Series([100, 120, 150])

    result = calculate_revenue_growth(revenue)

    assert result == pytest.approx(0.50)


def test_calculate_profit_margin():
    revenue = pd.Series([100, 120, 150])
    net_income = pd.Series([10, 15, 30])

    result = calculate_profit_margin(
        revenue,
        net_income,
    )

    assert result == pytest.approx(0.20)


def test_calculate_eps_growth():
    eps = pd.Series([5, 6, 7.5])

    result = calculate_eps_growth(eps)

    assert result == pytest.approx(0.50)


def test_calculate_price_to_earnings():
    result = calculate_price_to_earnings(
        price=300,
        eps=15,
    )

    assert result == pytest.approx(20.0)


def test_calculate_fundamental_score():
    result = calculate_fundamental_score(
        revenue_growth=0.50,
        profit_margin=0.20,
        eps_growth=0.50,
        pe_ratio=20,
    )

    assert result == pytest.approx(30.5)


def test_classify_strong_fundamentals():
    result = classify_fundamental_strength(
        fundamental_score=25
    )

    assert result == "Strong Fundamentals"


def test_classify_moderate_fundamentals():
    result = classify_fundamental_strength(
        fundamental_score=10
    )

    assert result == "Moderate Fundamentals"


def test_classify_weak_fundamentals():
    result = classify_fundamental_strength(
        fundamental_score=5
    )

    assert result == "Weak Fundamentals"


def test_empty_revenue_is_rejected():
    revenue = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_revenue_growth(revenue)


def test_single_revenue_value_is_rejected():
    revenue = pd.Series([100])

    with pytest.raises(ValueError):
        calculate_revenue_growth(revenue)


def test_negative_revenue_is_rejected():
    revenue = pd.Series([100, -120])

    with pytest.raises(ValueError):
        calculate_revenue_growth(revenue)


def test_empty_profit_margin_data_is_rejected():
    revenue = pd.Series(dtype=float)
    net_income = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_profit_margin(
            revenue,
            net_income,
        )


def test_mismatched_profit_margin_data_is_rejected():
    revenue = pd.Series([100, 120])
    net_income = pd.Series([10])

    with pytest.raises(ValueError):
        calculate_profit_margin(
            revenue,
            net_income,
        )


def test_negative_revenue_for_profit_margin_is_rejected():
    revenue = pd.Series([100, -120])
    net_income = pd.Series([10, 15])

    with pytest.raises(ValueError):
        calculate_profit_margin(
            revenue,
            net_income,
        )


def test_empty_eps_is_rejected():
    eps = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_eps_growth(eps)


def test_single_eps_value_is_rejected():
    eps = pd.Series([5])

    with pytest.raises(ValueError):
        calculate_eps_growth(eps)


def test_negative_eps_is_rejected():
    eps = pd.Series([5, -6])

    with pytest.raises(ValueError):
        calculate_eps_growth(eps)


def test_invalid_price_for_pe_is_rejected():
    with pytest.raises(ValueError):
        calculate_price_to_earnings(
            price=0,
            eps=10,
        )


def test_invalid_eps_for_pe_is_rejected():
    with pytest.raises(ValueError):
        calculate_price_to_earnings(
            price=100,
            eps=0,
        )


def test_invalid_pe_for_fundamental_score_is_rejected():
    with pytest.raises(ValueError):
        calculate_fundamental_score(
            revenue_growth=0.20,
            profit_margin=0.10,
            eps_growth=0.20,
            pe_ratio=0,
        )