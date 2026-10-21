import pandas as pd
import pytest

from app.data.api_provider import APIDataProvider
from app.data.data_loader import DataLoader
from app.data.data_provider import LocalDataProvider
from app.data.fallback_provider import FallbackDataProvider


def create_valid_market_data():

    return pd.DataFrame({
        "date": [
            "2026-01-01",
            "2026-01-02",
        ],
        "symbol": [
            "TCS",
            "TCS",
        ],
        "open": [
            3500,
            3520,
        ],
        "high": [
            3540,
            3560,
        ],
        "low": [
            3480,
            3500,
        ],
        "close": [
            3520,
            3550,
        ],
        "volume": [
            120000,
            125000,
        ],
    })


def create_fallback_provider(
    monkeypatch,
    local_provider,
    api_provider,
):
    return FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )


def test_local_data_is_used_first(
    tmp_path,
    monkeypatch,
):

    file_path = tmp_path / "market_data.csv"

    data = create_valid_market_data()

    data.to_csv(
        file_path,
        index=False,
    )

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader
    )

    api_provider = APIDataProvider.__new__(
        APIDataProvider
    )

    def api_should_not_be_called(symbol):
        raise AssertionError(
            "API should not be called when "
            "local data is valid."
        )

    api_provider.get_market_data = (
        api_should_not_be_called
    )

    provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    result = provider.get_market_data(
        symbol="TCS",
        local_file_path=str(file_path),
    )

    assert len(result) == 2

    assert result["symbol"].iloc[0] == "TCS"


def test_api_is_used_when_local_file_is_missing(
    tmp_path,
    monkeypatch,
):

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader
    )

    api_provider = APIDataProvider.__new__(
        APIDataProvider
    )

    def fake_api(symbol):

        assert symbol == "TCS"

        return create_valid_market_data()

    api_provider.get_market_data = fake_api

    provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    result = provider.get_market_data(
        symbol="TCS",
        local_file_path=str(
            tmp_path / "missing.csv"
        ),
    )

    assert len(result) == 2

    assert result["symbol"].iloc[0] == "TCS"


def test_api_is_used_when_local_data_is_invalid(
    tmp_path,
):

    file_path = tmp_path / "invalid.csv"

    data = create_valid_market_data()

    data.loc[0, "close"] = -100

    data.to_csv(
        file_path,
        index=False,
    )

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader
    )

    api_provider = APIDataProvider.__new__(
        APIDataProvider
    )

    def fake_api(symbol):

        assert symbol == "TCS"

        return create_valid_market_data()

    api_provider.get_market_data = fake_api

    provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    result = provider.get_market_data(
        symbol="TCS",
        local_file_path=str(file_path),
    )

    assert len(result) == 2

    assert (
        result["close"] > 0
    ).all()


def test_api_is_used_when_symbol_is_missing_locally(
    tmp_path,
):

    file_path = tmp_path / "market_data.csv"

    data = create_valid_market_data()

    data.to_csv(
        file_path,
        index=False,
    )

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader
    )

    api_provider = APIDataProvider.__new__(
        APIDataProvider
    )

    def fake_api(symbol):

        assert symbol == "AAPL"

        return pd.DataFrame({
            "date": pd.to_datetime([
                "2026-01-01",
            ]),
            "symbol": [
                "AAPL",
            ],
            "open": [
                250,
            ],
            "high": [
                255,
            ],
            "low": [
                245,
            ],
            "close": [
                252,
            ],
            "volume": [
                100000,
            ],
        })

    api_provider.get_market_data = fake_api

    provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    result = provider.get_market_data(
        symbol="AAPL",
        local_file_path=str(file_path),
    )

    assert len(result) == 1

    assert result["symbol"].iloc[0] == "AAPL"


def test_both_sources_failure_is_propagated(
    tmp_path,
):

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader
    )

    api_provider = APIDataProvider.__new__(
        APIDataProvider
    )

    def fake_api(symbol):

        raise ConnectionError(
            "API unavailable."
        )

    api_provider.get_market_data = fake_api

    provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    with pytest.raises(ConnectionError):
        provider.get_market_data(
            symbol="TCS",
            local_file_path=str(
                tmp_path / "missing.csv"
            ),
        )