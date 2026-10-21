import pandas as pd

from app.data.data_loader import DataLoader


def test_load_csv(tmp_path):

    file_path = tmp_path / "stocks.csv"

    file_path.write_text(
        "symbol,price\n"
        "TCS,3500\n"
        "INFY,1600\n"
    )

    loader = DataLoader()

    data = loader.load_csv(
        str(file_path)
    )

    assert isinstance(data, pd.DataFrame)

    assert len(data) == 2

    assert list(data.columns) == [
        "symbol",
        "price",
    ]

    assert data.iloc[0]["symbol"] == "TCS"


def test_missing_file_raises_error():

    loader = DataLoader()

    try:
        loader.load_csv(
            "data/nonexistent.csv"
        )
        assert False
    except FileNotFoundError:
        assert True


def test_valid_market_data():

    loader = DataLoader()

    data = loader.load_csv(
        "data/market_data.csv"
    )

    validated_data = loader.validate_market_data(
        data
    )

    assert len(validated_data) == 10

    assert validated_data["date"].dtype.kind == "M"


def test_missing_column_is_rejected():

    loader = DataLoader()

    data = pd.DataFrame({
        "date": ["2026-01-01"],
        "symbol": ["TCS"],
        "open": [3500],
        "high": [3550],
        "low": [3480],
        "close": [3520],
    })

    try:
        loader.validate_market_data(data)
        assert False
    except ValueError as error:
        assert "volume" in str(error)


def test_negative_price_is_rejected():

    loader = DataLoader()

    data = pd.DataFrame({
        "date": ["2026-01-01"],
        "symbol": ["TCS"],
        "open": [-3500],
        "high": [3550],
        "low": [3480],
        "close": [3520],
        "volume": [120000],
    })

    try:
        loader.validate_market_data(data)
        assert False
    except ValueError as error:
        assert "Prices must be greater than zero" in str(error)


def test_invalid_ohlc_is_rejected():

    loader = DataLoader()

    data = pd.DataFrame({
        "date": ["2026-01-01"],
        "symbol": ["TCS"],
        "open": [3500],
        "high": [3400],
        "low": [3480],
        "close": [3520],
        "volume": [120000],
    })

    try:
        loader.validate_market_data(data)
        assert False
    except ValueError as error:
        assert "OHLC" in str(error)