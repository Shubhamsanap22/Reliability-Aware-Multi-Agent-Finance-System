import pandas as pd
import pytest

from app.data.data_loader import DataLoader
from app.data.data_provider import LocalDataProvider


def create_valid_market_data():
    return pd.DataFrame({
        "date": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-05",
        ],
        "symbol": [
            "TCS",
            "TCS",
            "TCS",
        ],
        "open": [
            3500,
            3520,
            3550,
        ],
        "high": [
            3540,
            3560,
            3580,
        ],
        "low": [
            3480,
            3500,
            3520,
        ],
        "close": [
            3520,
            3550,
            3570,
        ],
        "volume": [
            120000,
            125000,
            130000,
        ],
    })


def test_local_data_provider_loads_valid_data(
    tmp_path,
):
    file_path = tmp_path / "market_data.csv"

    data = create_valid_market_data()

    data.to_csv(
        file_path,
        index=False,
    )

    loader = DataLoader()

    provider = LocalDataProvider(
        data_loader=loader
    )

    result = provider.get_market_data(
        str(file_path)
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) == 3

    assert list(result.columns) == [
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]


def test_local_data_provider_validates_data(
    tmp_path,
):
    file_path = tmp_path / "invalid_data.csv"

    data = create_valid_market_data()

    data.loc[1, "close"] = -100

    data.to_csv(
        file_path,
        index=False,
    )

    loader = DataLoader()

    provider = LocalDataProvider(
        data_loader=loader
    )

    with pytest.raises(ValueError):
        provider.get_market_data(
            str(file_path)
        )


def test_local_data_provider_missing_file(
    tmp_path,
):
    file_path = tmp_path / "missing.csv"

    loader = DataLoader()

    provider = LocalDataProvider(
        data_loader=loader
    )

    with pytest.raises(FileNotFoundError):
        provider.get_market_data(
            str(file_path)
        )
        