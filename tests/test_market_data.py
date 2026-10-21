import pandas as pd

from app.data.data_loader import DataLoader


def test_market_data_structure():

    loader = DataLoader()

    data = loader.load_csv(
        "data/market_data.csv"
    )

    expected_columns = [
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    assert list(data.columns) == expected_columns

    assert len(data) == 10

    assert data["symbol"].nunique() == 2


def test_market_data_contains_required_symbols():

    loader = DataLoader()

    data = loader.load_csv(
        "data/market_data.csv"
    )

    symbols = set(
        data["symbol"]
    )

    assert "TCS" in symbols
    assert "INFY" in symbols