from app.calculations.risk_classifier import classify_risk


def test_low_risk():

    result = classify_risk(
        volatility=0.10,
        max_drawdown=-0.05,
    )

    assert result == "Low"


def test_moderate_risk_from_volatility():

    result = classify_risk(
        volatility=0.20,
        max_drawdown=-0.05,
    )

    assert result == "Moderate"


def test_moderate_risk_from_drawdown():

    result = classify_risk(
        volatility=0.10,
        max_drawdown=-0.20,
    )

    assert result == "Moderate"


def test_high_risk_from_volatility():

    result = classify_risk(
        volatility=0.35,
        max_drawdown=-0.05,
    )

    assert result == "High"


def test_high_risk_from_drawdown():

    result = classify_risk(
        volatility=0.10,
        max_drawdown=-0.35,
    )

    assert result == "High"


def test_exact_moderate_boundary():

    result = classify_risk(
        volatility=0.15,
        max_drawdown=-0.05,
    )

    assert result == "Moderate"


def test_exact_high_boundary():

    result = classify_risk(
        volatility=0.30,
        max_drawdown=-0.05,
    )

    assert result == "High"