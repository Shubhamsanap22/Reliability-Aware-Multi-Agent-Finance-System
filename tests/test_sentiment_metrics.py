import pandas as pd
import pytest

from app.calculations.sentiment_metrics import (
    calculate_average_sentiment,
    calculate_sentiment_score,
    calculate_sentiment_strength,
    calculate_sentiment_trend,
    classify_sentiment,
    classify_sentiment_signal,
    classify_sentiment_strength,
)


def test_calculate_average_sentiment():
    scores = pd.Series(
        [-0.2, 0.4, 0.6]
    )

    result = calculate_average_sentiment(
        scores
    )

    assert result == pytest.approx(0.2667, rel=1e-3)


def test_average_sentiment_rejects_empty_data():
    with pytest.raises(ValueError):
        calculate_average_sentiment(
            pd.Series(dtype=float)
        )


def test_average_sentiment_rejects_invalid_scores():
    scores = pd.Series(
        [-0.2, 1.5]
    )

    with pytest.raises(ValueError):
        calculate_average_sentiment(
            scores
        )


def test_classify_positive_sentiment():
    assert classify_sentiment(0.50) == "Positive"


def test_classify_negative_sentiment():
    assert classify_sentiment(-0.50) == "Negative"


def test_classify_neutral_sentiment():
    assert classify_sentiment(0.05) == "Neutral"


def test_calculate_sentiment_strength():
    assert calculate_sentiment_strength(
        -0.75
    ) == pytest.approx(0.75)


def test_classify_strong_sentiment():
    assert classify_sentiment_strength(
        0.80
    ) == "Strong"


def test_classify_moderate_sentiment():
    assert classify_sentiment_strength(
        0.40
    ) == "Moderate"


def test_classify_weak_sentiment():
    assert classify_sentiment_strength(
        0.10
    ) == "Weak"


def test_calculate_improving_sentiment_trend():
    scores = pd.Series(
        [-0.4, -0.1, 0.2, 0.5]
    )

    assert calculate_sentiment_trend(
        scores
    ) == "Improving"


def test_calculate_weakening_sentiment_trend():
    scores = pd.Series(
        [0.5, 0.2, -0.1, -0.4]
    )

    assert calculate_sentiment_trend(
        scores
    ) == "Weakening"


def test_calculate_stable_sentiment_trend():
    scores = pd.Series(
        [0.2, 0.2, 0.2]
    )

    assert calculate_sentiment_trend(
        scores
    ) == "Stable"


def test_sentiment_trend_requires_two_values():
    scores = pd.Series([0.2])

    with pytest.raises(ValueError):
        calculate_sentiment_trend(
            scores
        )


def test_calculate_sentiment_score():
    result = calculate_sentiment_score(
        average_sentiment=0.50,
        sentiment_strength=0.80,
    )

    assert result == pytest.approx(57.5)


def test_classify_strong_positive_signal():
    assert classify_sentiment_signal(
        40
    ) == "Strong Positive Sentiment"


def test_classify_moderate_positive_signal():
    assert classify_sentiment_signal(
        20
    ) == "Moderate Positive Sentiment"


def test_classify_neutral_signal():
    assert classify_sentiment_signal(
        0
    ) == "Neutral Sentiment"


def test_classify_moderate_negative_signal():
    assert classify_sentiment_signal(
        -20
    ) == "Moderate Negative Sentiment"


def test_classify_strong_negative_signal():
    assert classify_sentiment_signal(
        -40
    ) == "Strong Negative Sentiment"