import pandas as pd


def calculate_price_trend(
    prices: pd.Series,
) -> str:
    """Classify the historical price trend."""

    if prices.empty:
        raise ValueError("Price data cannot be empty.")

    if len(prices) < 2:
        raise ValueError(
            "At least two prices are required."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    first_price = float(prices.iloc[0])
    last_price = float(prices.iloc[-1])

    if last_price > first_price:
        return "Upward"

    if last_price < first_price:
        return "Downward"

    return "Sideways"


def calculate_volume_trend(
    volume: pd.Series,
) -> str:
    """Classify the historical trading-volume trend."""

    if volume.empty:
        raise ValueError(
            "Volume data cannot be empty."
        )

    if (volume < 0).any():
        raise ValueError(
            "Volume cannot be negative."
        )

    if len(volume) < 2:
        raise ValueError(
            "At least two volume values are required."
        )

    first_volume = float(volume.iloc[0])
    last_volume = float(volume.iloc[-1])

    if last_volume > first_volume:
        return "Increasing"

    if last_volume < first_volume:
        return "Decreasing"

    return "Stable"


def calculate_total_return(
    prices: pd.Series,
) -> float:
    """Calculate total historical price return."""

    if prices.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    if len(prices) < 2:
        raise ValueError(
            "At least two prices are required."
        )

    return float(
        (prices.iloc[-1] / prices.iloc[0]) - 1
    )


def calculate_average_volume(
    volume: pd.Series,
) -> float:
    """Calculate average trading volume."""

    if volume.empty:
        raise ValueError(
            "Volume data cannot be empty."
        )

    if (volume < 0).any():
        raise ValueError(
            "Volume cannot be negative."
        )

    return float(volume.mean())


def classify_market_trend(
    price_trend: str,
    volume_trend: str,
) -> str:
    """
    Classify the overall market trend using price
    and volume direction.
    """

    if (
        price_trend == "Upward"
        and volume_trend == "Increasing"
    ):
        return "Strong Upward Trend"

    if (
        price_trend == "Upward"
        and volume_trend != "Increasing"
    ):
        return "Moderate Upward Trend"

    if (
        price_trend == "Downward"
        and volume_trend == "Increasing"
    ):
        return "Strong Downward Trend"

    if (
        price_trend == "Downward"
        and volume_trend != "Increasing"
    ):
        return "Moderate Downward Trend"

    return "Sideways Trend"