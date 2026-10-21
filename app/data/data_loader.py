from pathlib import Path

import pandas as pd


class DataLoader:
    """Loads and validates financial market data."""

    REQUIRED_COLUMNS = [
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load a CSV file into a pandas DataFrame."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Data file not found: {file_path}"
            )

        return pd.read_csv(path)

    def validate_market_data(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Validate the structure and values of market data."""

        # Check required columns
        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        # Check for missing values
        if data[self.REQUIRED_COLUMNS].isnull().any().any():
            raise ValueError(
                "Market data contains missing values."
            )

        # Convert date column
        try:
            data["date"] = pd.to_datetime(data["date"])
        except (ValueError, TypeError):
            raise ValueError(
                "Invalid date values in market data."
            )

        # Check numeric columns
        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        for column in numeric_columns:
            if not pd.api.types.is_numeric_dtype(
                data[column]
            ):
                raise ValueError(
                    f"Column '{column}' must contain numeric values."
                )

        # Prices must be positive
        price_columns = [
            "open",
            "high",
            "low",
            "close",
        ]

        if (data[price_columns] <= 0).any().any():
            raise ValueError(
                "Prices must be greater than zero."
            )

        # Volume cannot be negative
        if (data["volume"] < 0).any():
            raise ValueError(
                "Volume cannot be negative."
            )

        # Validate OHLC relationships
        if (
            (data["high"] < data["open"])
            | (data["high"] < data["close"])
            | (data["low"] > data["open"])
            | (data["low"] > data["close"])
        ).any():
            raise ValueError(
                "Invalid OHLC relationship in market data."
            )

        return data