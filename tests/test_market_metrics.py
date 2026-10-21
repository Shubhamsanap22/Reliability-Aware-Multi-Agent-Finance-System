import pandas as pd
import pytest

from app.calculations.market_metrics import (
    calculate_average_volume,
    calculate_price_trend,
    calculate_total_return,
    calculate_volume_trend,
    classify_market_trend,
)


def test_calculate_price_trend_upward():
    prices = pd.Series([100, 105, 110, 120])

    result = calculate_price_trend(prices)

    assert result == "Upward"


def test_calculate_price_trend_downward():
    prices = pd.Series([120, 115, 110, 100])

    result = calculate_price_trend(prices)

    assert result == "Downward"


def test_calculate_price_trend_sideways():
    prices = pd.Series([100, 100, 100, 100])

    result = calculate_price_trend(prices)

    assert result == "Sideways"


def test_calculate_volume_trend_increasing():
    volume = pd.Series([1000, 1200, 1500, 2000])

    result = calculate_volume_trend(volume)

    assert result == "Increasing"


def test_calculate_volume_trend_decreasing():
    volume = pd.Series([2000, 1500, 1200, 1000])

    result = calculate_volume_trend(volume)

    assert result == "Decreasing"


def test_calculate_volume_trend_stable():
    volume = pd.Series([1000, 1000, 1000, 1000])

    result = calculate_volume_trend(volume)

    assert result == "Stable"


def test_calculate_total_return():
    prices = pd.Series([100, 110, 120])

    result = calculate_total_return(prices)

    assert result == pytest.approx(0.20)


def test_calculate_average_volume():
    volume = pd.Series([1000, 2000, 3000])

    result = calculate_average_volume(volume)

    assert result == pytest.approx(2000.0)


def test_classify_strong_upward_trend():
    result = classify_market_trend(
        price_trend="Upward",
        volume_trend="Increasing",
    )

    assert result == "Strong Upward Trend"


def test_classify_moderate_upward_trend():
    result = classify_market_trend(
        price_trend="Upward",
        volume_trend="Stable",
    )

    assert result == "Moderate Upward Trend"


def test_classify_strong_downward_trend():
    result = classify_market_trend(
        price_trend="Downward",
        volume_trend="Increasing",
    )

    assert result == "Strong Downward Trend"


def test_classify_moderate_downward_trend():
    result = classify_market_trend(
        price_trend="Downward",
        volume_trend="Decreasing",
    )

    assert result == "Moderate Downward Trend"


def test_classify_sideways_trend():
    result = classify_market_trend(
        price_trend="Sideways",
        volume_trend="Stable",
    )

    assert result == "Sideways Trend"


def test_empty_prices_are_rejected():
    prices = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_price_trend(prices)


def test_single_price_is_rejected():
    prices = pd.Series([100])

    with pytest.raises(ValueError):
        calculate_price_trend(prices)


def test_negative_prices_are_rejected():
    prices = pd.Series([100, -110, 120])

    with pytest.raises(ValueError):
        calculate_price_trend(prices)


def test_empty_volume_is_rejected():
    volume = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_volume_trend(volume)


def test_negative_volume_is_rejected():
    volume = pd.Series([1000, -500, 2000])

    with pytest.raises(ValueError):
        calculate_volume_trend(volume)


def test_single_volume_value_is_rejected():
    volume = pd.Series([1000])

    with pytest.raises(ValueError):
        calculate_volume_trend(volume)


def test_empty_prices_are_rejected_for_total_return():
    prices = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_total_return(prices)


def test_single_price_is_rejected_for_total_return():
    prices = pd.Series([100])

    with pytest.raises(ValueError):
        calculate_total_return(prices)


def test_negative_prices_are_rejected_for_total_return():
    prices = pd.Series([100, -110])

    with pytest.raises(ValueError):
        calculate_total_return(prices)


def test_empty_volume_is_rejected_for_average_volume():
    volume = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        calculate_average_volume(volume)


def test_negative_volume_is_rejected_for_average_volume():
    volume = pd.Series([1000, -500])

    with pytest.raises(ValueError):
        calculate_average_volume(volume)