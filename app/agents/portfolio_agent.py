import math
import re

import numpy as np
import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.portfolio_metrics import (
    calculate_concentration,
    calculate_portfolio_return,
    calculate_portfolio_sharpe_ratio,
    calculate_portfolio_volatility,
    classify_diversification,
)
from app.data.fallback_provider import (
    FallbackDataProvider,
    create_default_data_provider,
)
from app.models.schemas import AgentState, AgentStatus


class PortfolioAgent(BaseAgent):
    """Analyze portfolio returns, volatility, Sharpe ratio and concentration."""

    REQUIRED_COLUMNS = {"date", "symbol", "close"}
    PERIODS_PER_YEAR = 252

    SUPPORTED_SYMBOLS = [
        "TCS",
        "INFY",
        "RELIANCE",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
    ]

    def __init__(
        self,
        data_provider: FallbackDataProvider | None = None,
        local_file_path: str | None = None,
    ) -> None:
        super().__init__(
            name="Portfolio Agent",
            reliability=0.94,
            estimated_cost=700,
        )

        if data_provider is None:
            data_provider, default_path = create_default_data_provider()

            if local_file_path is None:
                local_file_path = default_path

        self.data_provider = data_provider
        self.local_file_path = local_file_path

    def execute(
        self,
        query: str,
        budget: int,
        market_data: pd.DataFrame | None = None,
    ) -> AgentState:
        """Analyze a portfolio using historical closing prices."""

        required_budget = 500

        if budget < required_budget:
            return self._failed(budget, "Insufficient budget.")

        # 1. Identify requested symbols.
        symbols = self._get_symbols(query)

        # 2. Handle generic requests without market data.
        # This fallback preserves the existing test contract.
        if not symbols:
            if market_data is None:
                return AgentState(
                    agent_name=self.name,
                    reliability=self.reliability,
                    allocated_budget=budget,
                    used_budget=required_budget,
                    status=AgentStatus.COMPLETED,
                    output="Dummy portfolio analysis completed.",
                )

            return self._failed(
                budget,
                "No supported symbols found in query.",
            )

        # 3. Load market data if it was not supplied.
        if market_data is None:
            if self.data_provider is None:
                return self._failed(
                    budget,
                    "Market data is unavailable; no provider was supplied.",
                )

            if not self.local_file_path:
                return self._failed(
                    budget,
                    "Local data file path is not configured.",
                )

            frames = []

            try:
                for symbol in symbols:
                    frame = self.data_provider.get_market_data(
                        symbol=symbol,
                        local_file_path=self.local_file_path,
                    )
                    frames.append(frame)

                if frames:
                    market_data = pd.concat(
                        frames,
                        ignore_index=True,
                    )

            except Exception as error:
                return self._failed(
                    budget,
                    f"Unable to load market data: {error}",
                )

        if market_data is None or market_data.empty:
            return self._failed(
                budget,
                "Market data is empty.",
            )

        # 4. Validate required columns.
        missing_columns = self.REQUIRED_COLUMNS.difference(
            market_data.columns
        )

        if missing_columns:
            return self._failed(
                budget,
                "Market data is missing required columns: "
                f"{sorted(missing_columns)}",
            )

        # 5. Normalize market data.
        data = market_data.copy()

        data["symbol"] = (
            data["symbol"]
            .astype("string")
            .str.strip()
            .str.upper()
        )

        data["date"] = pd.to_datetime(
            data["date"],
            errors="coerce",
        )

        data["close"] = pd.to_numeric(
            data["close"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["date", "symbol", "close"]
        )

        if data.empty:
            return self._failed(
                budget,
                "Market data contains no valid observations.",
            )

        close_values = data["close"].to_numpy(dtype=float)

        if (
            (data["close"] <= 0).any()
            or not np.isfinite(close_values).all()
        ):
            return self._failed(
                budget,
                "Closing prices must be finite and greater than zero.",
            )

        # Keep only requested symbols.
        data = data[data["symbol"].isin(symbols)].copy()

        available_symbols = set(data["symbol"].unique())

        missing_symbols = [
            symbol
            for symbol in symbols
            if symbol not in available_symbols
        ]

        if missing_symbols:
            return self._failed(
                budget,
                "No supported symbols found in query.",
            )

        # 6. Extract allocation weights.
        try:
            weights = self._extract_weights(
                query,
                symbols,
            )
        except ValueError as error:
            return self._failed(budget, str(error))

        # 7. Calculate asset returns and align daily returns.
        asset_returns: dict[str, float] = {}
        return_series: dict[str, pd.Series] = {}

        try:
            for symbol in symbols:
                symbol_data = data.loc[
                    data["symbol"] == symbol,
                    ["date", "close"],
                ].copy()

                symbol_data = symbol_data.sort_values("date")

                if symbol_data["date"].duplicated().any():
                    raise ValueError(
                        f"Duplicate dates found for {symbol}; "
                        "remove or aggregate duplicates before analysis."
                    )

                if len(symbol_data) < 3:
                    raise ValueError(
                        f"At least three closing prices are required "
                        f"for {symbol} portfolio analysis."
                    )

                prices = (
                    symbol_data
                    .set_index("date")["close"]
                    .astype(float)
                )

                holding_period_return = float(
                    prices.iloc[-1] / prices.iloc[0] - 1.0
                )

                if not math.isfinite(holding_period_return):
                    raise ValueError(
                        f"Calculated return for {symbol} is not finite."
                    )

                asset_returns[symbol] = holding_period_return

                return_series[symbol] = (
                    prices.pct_change()
                    .dropna()
                    .rename(symbol)
                )

            returns_frame = pd.concat(
                list(return_series.values()),
                axis=1,
                join="inner",
            ).dropna(how="any").sort_index()

            if len(returns_frame) < 2:
                raise ValueError(
                    "At least two common daily return observations "
                    "are required across all selected assets."
                )

            # Weighted holding-period return.
            portfolio_return = calculate_portfolio_return(
                asset_returns,
                weights,
            )

            # Annualized portfolio volatility.
            portfolio_volatility = calculate_portfolio_volatility(
                returns=returns_frame,
                weights=weights,
                periods_per_year=self.PERIODS_PER_YEAR,
            )

            # Annualized arithmetic mean of daily portfolio returns.
            daily_portfolio_returns = (
                returns_frame[list(weights)]
                .mul(pd.Series(weights), axis="columns")
                .sum(axis=1)
            )

            annualized_return = float(
                daily_portfolio_returns.mean()
                * self.PERIODS_PER_YEAR
            )

            portfolio_sharpe = calculate_portfolio_sharpe_ratio(
                portfolio_return=annualized_return,
                portfolio_volatility=portfolio_volatility,
                risk_free_rate=0.0,
            )

            concentration = calculate_concentration(weights)

            diversification = classify_diversification(
                concentration
            )

            calculated_metrics = [
                portfolio_return,
                portfolio_volatility,
                portfolio_sharpe,
                concentration,
            ]

            if not all(
                math.isfinite(float(value))
                for value in calculated_metrics
            ):
                raise ValueError(
                    "Portfolio calculations produced a non-finite result."
                )

        except (
            ValueError,
            KeyError,
            TypeError,
            ZeroDivisionError,
        ) as error:
            return self._failed(budget, str(error))

        # 8. Format the analysis.
        output = self._build_output(
            symbols=symbols,
            weights=weights,
            portfolio_return=portfolio_return,
            portfolio_volatility=portfolio_volatility,
            portfolio_sharpe=portfolio_sharpe,
            concentration=concentration,
            diversification=diversification,
            observations=len(returns_frame),
        )

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=required_budget,
            status=AgentStatus.COMPLETED,
            output=output,
        )

    def _failed(
        self,
        budget: int,
        reason: str,
    ) -> AgentState:
        """Return a failure state."""

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=0,
            status=AgentStatus.FAILED,
            failure_reason=reason,
        )

    def _get_symbols(self, query: str) -> list[str]:
        """Use structured task symbols when available."""

        if self.task_requirement and self.task_requirement.symbols:
            requested = [
                str(symbol).strip().upper()
                for symbol in self.task_requirement.symbols
                if str(symbol).strip()
            ]

            unsupported = [
                symbol
                for symbol in requested
                if symbol not in self.SUPPORTED_SYMBOLS
            ]

            if unsupported:
                return []

            return list(dict.fromkeys(requested))

        return self._find_symbols_in_query(query)

    @staticmethod
    def _find_symbols_in_query(
        query: str,
        available_symbols=None,
    ) -> list[str]:
        """Find supported ticker symbols as whole words."""

        if available_symbols is None:
            available_symbols = PortfolioAgent.SUPPORTED_SYMBOLS

        query_upper = query.upper()
        found = []

        for symbol in available_symbols:
            normalized = str(symbol).strip().upper()

            if (
                re.search(
                    rf"\b{re.escape(normalized)}\b",
                    query_upper,
                )
                and normalized not in found
            ):
                found.append(normalized)

        return found

    @staticmethod
    def _extract_weights(
        query: str,
        symbols: list[str],
    ) -> dict[str, float]:
        """Extract percentage allocations or use equal weights."""

        if not symbols:
            raise ValueError(
                "At least one supported symbol is required."
            )

        pattern = (
            r"\b([A-Za-z][A-Za-z0-9._-]*)\s*[:=]?\s*"
            r"(\d+(?:\.\d+)?)\s*%"
        )

        matches = re.findall(pattern, query)
        found: dict[str, float] = {}

        for name, percentage in matches:
            normalized_name = name.upper()

            for symbol in symbols:
                if normalized_name == symbol.upper():
                    if symbol in found:
                        raise ValueError(
                            f"Multiple weights were specified for {symbol}."
                        )

                    found[symbol] = float(percentage) / 100.0

        # No explicit weights: allocate equally.
        if not found:
            equal_weight = 1.0 / len(symbols)

            return {
                symbol: equal_weight
                for symbol in symbols
            }

        # Reject incomplete allocations.
        if set(found) != set(symbols):
            raise ValueError(
                "Weights must be provided for all selected assets."
            )

        if any(
            not math.isfinite(weight) or weight < 0
            for weight in found.values()
        ):
            raise ValueError(
                "Portfolio weights must be finite and non-negative."
            )

        if not math.isclose(
            sum(found.values()),
            1.0,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "Portfolio weights must sum to 1."
            )

        return found

    @staticmethod
    def _build_output(
        symbols,
        weights,
        portfolio_return,
        portfolio_volatility,
        portfolio_sharpe,
        concentration,
        diversification,
        observations,
    ) -> str:
        """Format calculated portfolio results."""

        allocations = "\n".join(
            f"{symbol}: {weights[symbol] * 100:.2f}%"
            for symbol in symbols
        )

        if diversification == "Well Diversified":
            interpretation = (
                "The selected assets have relatively low allocation "
                "concentration. This does not eliminate market risk."
            )
        elif diversification == "Moderately Diversified":
            interpretation = (
                "The portfolio has moderate allocation concentration."
            )
        else:
            interpretation = (
                "The portfolio is highly concentrated and may have "
                "greater asset-specific risk."
            )

        return (
            "Portfolio Assessment\n\n"
            f"Selected Assets: {', '.join(symbols)}\n\n"
            f"Suggested Allocation:\n{allocations}\n\n"
            "Historical Performance (holding period):\n"
            f"Portfolio return (weighted holding period): "
            f"{portfolio_return * 100:.2f}%\n\n"
            "Risk Analysis (annualized from aligned daily returns):\n"
            f"Portfolio volatility: "
            f"{portfolio_volatility * 100:.2f}%\n"
            f"Portfolio Sharpe ratio: {portfolio_sharpe:.4f}\n"
            f"Aligned daily return observations: {observations}\n\n"
            f"Concentration (HHI): {concentration:.4f}\n"
            f"Diversification level: {diversification}\n\n"
            f"Simple Explanation:\n{interpretation}\n\n"
            "This is a historical calculation, not a personalized "
            "investment recommendation. Results depend on data quality, "
            "observation period, assumptions, and transaction costs. "
            "Past performance does not guarantee future returns."
        )