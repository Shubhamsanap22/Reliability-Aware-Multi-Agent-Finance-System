import math

import pandas as pd


def calculate_average_sentiment(sentiment_scores: pd.Series) -> float:
    """Calculate the mean of valid sentiment scores in [-1, 1]."""
    if sentiment_scores.empty:
        raise ValueError("Sentiment scores cannot be empty.")

    scores = pd.to_numeric(sentiment_scores, errors="coerce")

    if scores.isna().any() or not scores.map(math.isfinite).all():
        raise ValueError("Sentiment scores must be finite numeric values.")

    if ((scores < -1) | (scores > 1)).any():
        raise ValueError("Sentiment scores must be between -1 and 1.")

    return float(scores.mean())


def classify_sentiment(sentiment_score: float) -> str:
    """Classify sentiment as positive, neutral or negative."""
    if not math.isfinite(sentiment_score) or not -1 <= sentiment_score <= 1:
        raise ValueError("Sentiment score must be finite and between -1 and 1.")

    if sentiment_score >= 0.20:
        return "Positive"

    if sentiment_score <= -0.20:
        return "Negative"

    return "Neutral"


def calculate_sentiment_strength(sentiment_score: float) -> float:
    """Return the absolute magnitude of a sentiment score."""
    if not math.isfinite(sentiment_score) or not -1 <= sentiment_score <= 1:
        raise ValueError("Sentiment score must be finite and between -1 and 1.")

    return float(abs(sentiment_score))


def classify_sentiment_strength(strength: float) -> str:
    """Classify sentiment magnitude."""
    if not math.isfinite(strength) or not 0 <= strength <= 1:
        raise ValueError("Sentiment strength must be between 0 and 1.")

    if strength >= 0.60:
        return "Strong"

    if strength >= 0.30:
        return "Moderate"

    return "Weak"


def calculate_sentiment_trend(sentiment_scores: pd.Series) -> str:
    """Determine whether the sentiment score is improving or weakening."""
    if sentiment_scores.empty:
        raise ValueError("Sentiment scores cannot be empty.")

    if len(sentiment_scores) < 2:
        raise ValueError("At least two sentiment scores are required.")

    scores = pd.to_numeric(sentiment_scores, errors="coerce")

    if scores.isna().any() or not scores.map(math.isfinite).all():
        raise ValueError("Sentiment scores must be finite numeric values.")

    if ((scores < -1) | (scores > 1)).any():
        raise ValueError("Sentiment scores must be between -1 and 1.")

    first_score = float(scores.iloc[0])
    last_score = float(scores.iloc[-1])

    if last_score > first_score:
        return "Improving"

    if last_score < first_score:
        return "Weakening"

    return "Stable"


def calculate_sentiment_score(
    average_sentiment: float,
    sentiment_strength: float,
) -> float:
    """
    Calculate the project's heuristic sentiment score.

    Positive and negative sentiment retain their respective signs.
    This is a project-defined score, not a standard financial metric.
    """
    if (
        not math.isfinite(average_sentiment)
        or not -1 <= average_sentiment <= 1
    ):
        raise ValueError(
            "Average sentiment must be finite and between -1 and 1."
        )

    if (
        not math.isfinite(sentiment_strength)
        or not 0 <= sentiment_strength <= 1
    ):
        raise ValueError(
            "Sentiment strength must be finite and between 0 and 1."
        )

    if average_sentiment == 0:
        return 0.0

    signed_strength = math.copysign(
        sentiment_strength,
        average_sentiment,
    )

    return float(
        average_sentiment * 75
        + signed_strength * 25
    )


def classify_sentiment_signal(sentiment_score: float) -> str:
    """Classify the project's overall sentiment score."""
    if not math.isfinite(sentiment_score):
        raise ValueError("Sentiment score must be finite.")

    if sentiment_score >= 35:
        return "Strong Positive Sentiment"

    if sentiment_score >= 10:
        return "Moderate Positive Sentiment"

    if sentiment_score > -10:
        return "Neutral Sentiment"

    if sentiment_score > -35:
        return "Moderate Negative Sentiment"

    return "Strong Negative Sentiment"