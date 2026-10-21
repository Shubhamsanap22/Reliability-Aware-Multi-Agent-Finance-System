
from pathlib import Path

import pandas as pd

from app.data.api_provider import APIDataProvider
from app.data.data_loader import DataLoader
from app.data.data_provider import LocalDataProvider


class FallbackDataProvider:
    """Retrieve market data from an API, with local CSV fallback."""

    def __init__(
        self,
        local_provider: LocalDataProvider,
        api_provider: APIDataProvider,
    ) -> None:
        self.local_provider = local_provider
        self.api_provider = api_provider

    def get_market_data(
        self,
        symbol: str,
        local_file_path: str | None = None,
    ) -> pd.DataFrame:
        """Try the API first, then fall back to local market data."""

        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must not be empty.")

        symbol = symbol.strip().upper()

        api_error: Exception | None = None

        try:
            api_data = self.api_provider.get_market_data(symbol)
            return self._validate_and_filter(
                api_data,
                symbol,
                "API",
            )
        except Exception as error:
            api_error = error

        if not local_file_path:
            raise RuntimeError(
                f"API request failed for {symbol}: {api_error}. "
                "No local fallback path was configured."
            ) from api_error

        try:
            local_data = self.local_provider.get_market_data(
                local_file_path
            )

            return self._validate_and_filter(
                local_data,
                symbol,
                "Local",
            )
        except Exception as local_error:
            # Preserve the API exception expected by callers/tests.
            assert api_error is not None
            raise api_error from local_error

    @staticmethod
    def _validate_and_filter(
        data: pd.DataFrame,
        symbol: str,
        source: str,
    ) -> pd.DataFrame:
        """Validate returned data and retain the requested symbol."""

        if not isinstance(data, pd.DataFrame):
            raise ValueError(
                f"{source} provider did not return a DataFrame."
            )

        if data.empty:
            raise ValueError(
                f"{source} provider returned empty market data."
            )

        required_columns = {"date", "symbol", "close"}
        missing_columns = required_columns.difference(data.columns)

        if missing_columns:
            raise ValueError(
                f"{source} data is missing required columns: "
                f"{sorted(missing_columns)}"
            )

        result = data.copy()

        result["symbol"] = result["symbol"].astype(str).str.upper()
        result["date"] = pd.to_datetime(
            result["date"],
            errors="coerce",
        )
        result["close"] = pd.to_numeric(
            result["close"],
            errors="coerce",
        )

        result = result.dropna(
            subset=["symbol", "date", "close"]
        )

        result = result[
            result["symbol"] == symbol
        ].copy()

        if result.empty:
            raise ValueError(
                f"{source} data contains no valid rows for {symbol}."
            )

        if not result["close"].map(
            lambda value: pd.notna(value)
            and value > 0
            and value != float("inf")
            and value != float("-inf")
        ).all():
            raise ValueError(
                f"{source} data contains invalid closing prices."
            )

        if result["date"].duplicated().any():
            raise ValueError(
                f"{source} data contains duplicate dates for {symbol}."
            )

        return result.sort_values("date").reset_index(drop=True)


def create_default_data_provider():
    """Create the default API/local provider and CSV path."""

    project_root = Path(__file__).resolve().parents[2]
    local_file_path = project_root / "data" / "market_data.csv"

    loader = DataLoader()

    local_provider = LocalDataProvider(
        data_loader=loader,
    )

    api_provider = APIDataProvider(
        data_loader=loader,
    )

    provider = FallbackDataProvider(
        local_provider=local_provider,
        api_provider=api_provider,
    )

    return provider, str(local_file_path)
