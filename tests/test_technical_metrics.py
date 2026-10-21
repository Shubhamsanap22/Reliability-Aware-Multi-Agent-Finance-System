import pandas as pd
import pytest

from app.calculations.technical_metrics import (
    calculate_price_momentum,
    calculate_rsi,
    calculate_simple_moving_average,
    calculate_technical_score,
    classify_price_position,
    classify_rsi,
    classify_technical_strength,
)


def test_calculate_simple_moving_average():
    prices = pd.Series(
        [10, 20, 30, 40, 50]
    )

    result = calculate_simple_moving_average(
        prices,
        window=3,
    )

    assert result == pytest.approx(40.0)


def test_sma_fails_with_empty_data():
    prices = pd.Series(
        dtype=float
    )

    with pytest.raises(ValueError):
        calculate_simple_moving_average(
            prices,
            window=3,
        )


def test_sma_fails_with_invalid_window():
    prices = pd.Series(
        [10, 20, 30]
    )

    with pytest.raises(ValueError):
        calculate_simple_moving_average(
            prices,
            window=0,
        )


def test_sma_fails_with_insufficient_data():
    prices = pd.Series(
        [10, 20]
    )

    with pytest.raises(ValueError):
        calculate_simple_moving_average(
            prices,
            window=3,
        )


def test_sma_fails_with_non_positive_prices():
    prices = pd.Series(
        [10, 0, 20]
    )

    with pytest.raises(ValueError):
        calculate_simple_moving_average(
            prices,
            window=2,
        )


def test_calculate_price_momentum():
    prices = pd.Series(
        [100, 105, 110, 120]
    )

    result = calculate_price_momentum(
        prices,
        lookback=2,
    )

    assert result == pytest.approx(
        (120 / 105) - 1
    )


def test_momentum_fails_with_invalid_lookback():
    prices = pd.Series(
        [100, 110, 120]
    )

    with pytest.raises(ValueError):
        calculate_price_momentum(
            prices,
            lookback=0,
        )


def test_momentum_fails_with_insufficient_data():
    prices = pd.Series(
        [100, 110]
    )

    with pytest.raises(ValueError):
        calculate_price_momentum(
            prices,
            lookback=2,
        )


def test_momentum_fails_with_non_positive_prices():
    prices = pd.Series(
        [100, 0, 110]
    )

    with pytest.raises(ValueError):
        calculate_price_momentum(
            prices,
            lookback=1,
        )


def test_calculate_rsi():
    prices = pd.Series(
        [
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
        ]
    )

    result = calculate_rsi(
        prices,
        period=14,
    )

    assert result == pytest.approx(100.0)


def test_rsi_fails_with_empty_data():
    prices = pd.Series(
        dtype=float
    )

    with pytest.raises(ValueError):
        calculate_rsi(
            prices,
            period=14,
        )


def test_rsi_fails_with_invalid_period():
    prices = pd.Series(
        [10, 11, 12]
    )

    with pytest.raises(ValueError):
        calculate_rsi(
            prices,
            period=0,
        )


def test_rsi_fails_with_insufficient_data():
    prices = pd.Series(
        [10, 11, 12]
    )

    with pytest.raises(ValueError):
        calculate_rsi(
            prices,
            period=14,
        )


def test_rsi_fails_with_non_positive_prices():
    prices = pd.Series(
        [10, 0, 12]
    )

    with pytest.raises(ValueError):
        calculate_rsi(
            prices,
            period=1,
        )


def test_classify_rsi_oversold():
    assert classify_rsi(25) == "Oversold"


def test_classify_rsi_overbought():
    assert classify_rsi(75) == "Overbought"


def test_classify_rsi_neutral():
    assert classify_rsi(50) == "Neutral"


def test_classify_price_position_above():
    assert classify_price_position(
        110,
        100,
    ) == "Above Moving Average"


def test_classify_price_position_below():
    assert classify_price_position(
        90,
        100,
    ) == "Below Moving Average"


def test_classify_price_position_equal():
    assert classify_price_position(
        100,
        100,
    ) == "At Moving Average"


def test_calculate_technical_score():
    result = calculate_technical_score(
        momentum=0.10,
        rsi=50,
        price_position="Above Moving Average",
    )

    assert result == pytest.approx(55.0)


def test_technical_score_fails_with_invalid_rsi():
    with pytest.raises(ValueError):
        calculate_technical_score(
            momentum=0.10,
            rsi=110,
            price_position="Above Moving Average",
        )


def test_classify_strong_technical_signals():
    assert classify_technical_strength(
        25
    ) == "Strong Technical Signals"


def test_classify_moderate_technical_signals():
    assert classify_technical_strength(
        10
    ) == "Moderate Technical Signals"


def test_classify_weak_technical_signals():
    assert classify_technical_strength(
        -5
    ) == "Weak Technical Signals"