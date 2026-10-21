import os

import pandas as pd
import requests
from dotenv import load_dotenv

from app.data.data_loader import DataLoader


class APIDataProvider:
    """Fetch and validate daily market data from Alpha Vantage."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, data_loader: DataLoader) -> None:
        # Load environment variables from .env.
        load_dotenv()

        self.data_loader = data_loader
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

        # Validate the API key during initialization.
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "ALPHA_VANTAGE_API_KEY is not configured."
            )

    def get_market_data(self, symbol: str) -> pd.DataFrame:
        """Fetch, parse, and validate daily market data."""

        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must not be empty.")

        symbol = symbol.strip().upper()

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": self.api_key,
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

        except requests.RequestException as error:
            raise ConnectionError(
                f"Market API request failed: {error}"
            ) from error

        except ValueError as error:
            raise ValueError(
                "Market API returned invalid JSON."
            ) from error

        if not isinstance(data, dict):
            raise ValueError("Unexpected market API response.")

        if "Error Message" in data:
            raise ValueError(
                f"API error for symbol '{symbol}'."
            )

        if "Note" in data or "Information" in data:
            raise RuntimeError(
                "Alpha Vantage rate limit or API notice received."
            )

        time_series = data.get("Time Series (Daily)")

        if not time_series:
            raise ValueError(
                f"No market data returned for '{symbol}'."
            )

        rows = []

        for date, values in time_series.items():
            try:
                rows.append(
                    {
                        "date": date,
                        "symbol": symbol,
                        "open": values["1. open"],
                        "high": values["2. high"],
                        "low": values["3. low"],
                        "close": values["4. close"],
                        "volume": values["5. volume"],
                    }
                )
            except (KeyError, TypeError) as error:
                raise ValueError(
                    f"Invalid market data fields for {symbol}."
                ) from error

        result = pd.DataFrame(rows)

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        for column in numeric_columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="raise",
            )

        result["date"] = pd.to_datetime(
            result["date"],
            errors="raise",
        )

        result = self.data_loader.validate_market_data(result)

        return result.sort_values("date").reset_index(drop=True)