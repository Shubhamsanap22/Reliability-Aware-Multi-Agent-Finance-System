import pandas as pd

from app.data.data_loader import DataLoader


class LocalDataProvider:
    """Provides validated financial data from local files."""

    def __init__(
        self,
        data_loader: DataLoader,
    ) -> None:
        self.data_loader = data_loader

    def get_market_data(
        self,
        file_path: str,
    ) -> pd.DataFrame:
        """Load and validate market data from a local file."""

        data = self.data_loader.load_csv(
            file_path
        )

        return self.data_loader.validate_market_data(
            data
        )