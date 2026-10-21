import pandas as pd


def calculate_simple_moving_average(
    prices: pd.Series,
    window: int = 20,
) -> float:
    """Calculate the latest simple moving average."""

    if prices.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    if window <= 0:
        raise ValueError(
            "Window must be greater than zero."
        )

    if len(prices) < window:
        raise ValueError(
            "Not enough price data for the requested window."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    return float(
        prices.rolling(window=window).mean().iloc[-1]
    )


def calculate_price_momentum(
    prices: pd.Series,
    lookback: int = 10,
) -> float:
    """Calculate price momentum over a lookback period."""

    if prices.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    if lookback <= 0:
        raise ValueError(
            "Lookback must be greater than zero."
        )

    if len(prices) <= lookback:
        raise ValueError(
            "Not enough price data for the requested lookback."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    return float(
        (prices.iloc[-1] / prices.iloc[-1 - lookback]) - 1
    )


def calculate_rsi(
    prices: pd.Series,
    period: int = 14,
) -> float:
    """Calculate the Relative Strength Index."""

    if prices.empty:
        raise ValueError(
            "Price data cannot be empty."
        )

    if period <= 0:
        raise ValueError(
            "Period must be greater than zero."
        )

    if len(prices) <= period:
        raise ValueError(
            "Not enough price data for RSI calculation."
        )

    if (prices <= 0).any():
        raise ValueError(
            "Prices must be greater than zero."
        )

    price_changes = prices.diff().dropna()

    gains = price_changes.clip(lower=0)
    losses = -price_changes.clip(upper=0)

    average_gain = gains.rolling(
        window=period
    ).mean().iloc[-1]

    average_loss = losses.rolling(
        window=period
    ).mean().iloc[-1]

    if average_loss == 0:
        return 100.0

    relative_strength = (
        average_gain / average_loss
    )

    return float(
        100 - (
            100 / (1 + relative_strength)
        )
    )


def classify_rsi(
    rsi: float,
) -> str:
    """Classify RSI into a simple technical interpretation."""

    if rsi < 30:
        return "Oversold"

    if rsi > 70:
        return "Overbought"

    return "Neutral"


def classify_price_position(
    price: float,
    moving_average: float,
) -> str:
    """Determine whether price is above or below its moving average."""

    if price > moving_average:
        return "Above Moving Average"

    if price < moving_average:
        return "Below Moving Average"

    return "At Moving Average"


def calculate_technical_score(
    momentum: float,
    rsi: float,
    price_position: str,
) -> float:
    """
    Calculate a project-specific technical score.

    Positive momentum and a price above its moving average
    increase the score. RSI contributes according to whether
    the market is in a neutral or extreme condition.
    """

    if rsi < 0 or rsi > 100:
        raise ValueError(
            "RSI must be between 0 and 100."
        )

    score = momentum * 50

    if price_position == "Above Moving Average":
        score += 25

    elif price_position == "Below Moving Average":
        score -= 25

    if 30 <= rsi <= 70:
        score += 25

    elif rsi < 30:
        score += 10

    else:
        score -= 10

    return float(score)


def classify_technical_strength(
    technical_score: float,
) -> str:
    """Classify overall technical strength."""

    if technical_score >= 20:
        return "Strong Technical Signals"

    if technical_score >= 0:
        return "Moderate Technical Signals"

    return "Weak Technical Signals"