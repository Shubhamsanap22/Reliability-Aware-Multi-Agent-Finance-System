import pandas as pd
import pytest

from app.data.api_provider import APIDataProvider
from app.data.data_loader import DataLoader


def create_api_response():

    return {
        "Meta Data": {
            "1. Information": "Daily Prices",
            "2. Symbol": "TCS",
        },
        "Time Series (Daily)": {
            "2026-01-02": {
                "1. open": "3520.00",
                "2. high": "3560.00",
                "3. low": "3500.00",
                "4. close": "3550.00",
                "5. volume": "125000",
            },
            "2026-01-01": {
                "1. open": "3500.00",
                "2. high": "3540.00",
                "3. low": "3480.00",
                "4. close": "3520.00",
                "5. volume": "120000",
            },
        },
    }


class FakeResponse:

    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


def test_api_provider_returns_market_data(
    monkeypatch,
):

    def fake_get(*args, **kwargs):
        return FakeResponse(
            create_api_response()
        )

    monkeypatch.setenv(
        "ALPHA_VANTAGE_API_KEY",
        "test-key",
    )

    monkeypatch.setattr(
        "app.data.api_provider.requests.get",
        fake_get,
    )

    provider = APIDataProvider(
        data_loader=DataLoader()
    )

    result = provider.get_market_data(
        "TCS"
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) == 2

    assert list(result.columns) == [
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    assert result["symbol"].iloc[0] == "TCS"


def test_api_provider_converts_numeric_columns(
    monkeypatch,
):

    def fake_get(*args, **kwargs):
        return FakeResponse(
            create_api_response()
        )

    monkeypatch.setenv(
        "ALPHA_VANTAGE_API_KEY",
        "test-key",
    )

    monkeypatch.setattr(
        "app.data.api_provider.requests.get",
        fake_get,
    )

    provider = APIDataProvider(
        data_loader=DataLoader()
    )

    result = provider.get_market_data(
        "TCS"
    )

    assert pd.api.types.is_numeric_dtype(
        result["open"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["high"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["low"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["close"]
    )

    assert pd.api.types.is_numeric_dtype(
        result["volume"]
    )


def test_api_error_is_handled(
    monkeypatch,
):

    def fake_get(*args, **kwargs):
        return FakeResponse({
            "Error Message": "Invalid API call."
        })

    monkeypatch.setenv(
        "ALPHA_VANTAGE_API_KEY",
        "test-key",
    )

    monkeypatch.setattr(
        "app.data.api_provider.requests.get",
        fake_get,
    )

    provider = APIDataProvider(
        data_loader=DataLoader()
    )

    with pytest.raises(ValueError):
        provider.get_market_data(
            "INVALID"
        )


def test_api_rate_limit_is_handled(
    monkeypatch,
):

    def fake_get(*args, **kwargs):
        return FakeResponse({
            "Note": (
                "API call frequency is limited."
            )
        })

    monkeypatch.setenv(
        "ALPHA_VANTAGE_API_KEY",
        "test-key",
    )

    monkeypatch.setattr(
        "app.data.api_provider.requests.get",
        fake_get,
    )

    provider = APIDataProvider(
        data_loader=DataLoader()
    )

    with pytest.raises(RuntimeError):
        provider.get_market_data(
            "TCS"
        )


def test_missing_api_key_is_rejected(
    monkeypatch,
):

    # Prevent the real .env file from
    # restoring the API key during the test.
    monkeypatch.setattr(
        "app.data.api_provider.load_dotenv",
        lambda: None,
    )

    monkeypatch.delenv(
        "ALPHA_VANTAGE_API_KEY",
        raising=False,
    )

    with pytest.raises(ValueError):
        APIDataProvider(
            data_loader=DataLoader()
        )