import math

import pandas as pd

from app.agents.base_agent import BaseAgent
from app.calculations.sentiment_metrics import (
    calculate_average_sentiment,
    calculate_sentiment_score,
    calculate_sentiment_strength,
    calculate_sentiment_trend,
    classify_sentiment,
    classify_sentiment_signal,
    classify_sentiment_strength,
)
from app.models.schemas import AgentState, AgentStatus


class SentimentAnalysisAgent(BaseAgent):
    """Analyze pre-scored financial news or other sentiment observations."""

    def __init__(self) -> None:
        super().__init__(
            name="Sentiment Analysis Agent",
            reliability=0.88,
            estimated_cost=650,
        )

    def execute(
        self,
        query: str,
        budget: int,
        sentiment_data: pd.DataFrame | None = None,
    ) -> AgentState:
        required_budget = 450

        if budget < required_budget:
            return self._failed(budget, "Insufficient budget.")

        if sentiment_data is None:
            return self._failed(
                budget,
                "Sentiment data is unavailable. Supply scored news or "
                "sentiment observations with symbol and sentiment_score columns.",
            )

        if sentiment_data.empty:
            return self._failed(budget, "Sentiment data is empty.")

        required_columns = {"symbol", "sentiment_score"}
        missing = required_columns.difference(sentiment_data.columns)

        if missing:
            return self._failed(
                budget,
                f"Sentiment data is missing required columns: {sorted(missing)}",
            )

        symbol = self._get_preferred_symbol(
            query=query,
            available_symbols=sentiment_data["symbol"].unique(),
        )

        if symbol is None:
            return self._failed(
                budget,
                "No supported symbol found in query.",
            )

        data = sentiment_data.copy()
        data["symbol"] = data["symbol"].astype(str).str.upper()

        symbol_data = data.loc[
            data["symbol"] == symbol.upper()
        ].copy()

        if symbol_data.empty:
            return self._failed(
                budget,
                f"No sentiment data found for {symbol}.",
            )

        if "date" in symbol_data.columns:
            symbol_data["date"] = pd.to_datetime(
                symbol_data["date"],
                errors="coerce",
            )

            if symbol_data["date"].isna().any():
                return self._failed(
                    budget,
                    "Sentiment data contains invalid dates.",
                )

            symbol_data = symbol_data.sort_values("date")

        scores = pd.to_numeric(
            symbol_data["sentiment_score"],
            errors="coerce",
        )

        if scores.isna().any() or not scores.map(math.isfinite).all():
            return self._failed(
                budget,
                "Sentiment scores must be finite numeric values.",
            )

        # Expected sentiment range is [-1, 1].
        if ((scores < -1) | (scores > 1)).any():
            return self._failed(
                budget,
                "Sentiment scores must be between -1 and 1.",
            )

        try:
            average_sentiment = calculate_average_sentiment(scores)
            sentiment_classification = classify_sentiment(
                average_sentiment
            )

            sentiment_strength = calculate_sentiment_strength(
                average_sentiment
            )
            strength_classification = classify_sentiment_strength(
                sentiment_strength
            )

            sentiment_trend = calculate_sentiment_trend(scores)

            overall_score = calculate_sentiment_score(
                average_sentiment=average_sentiment,
                sentiment_strength=sentiment_strength,
            )
            sentiment_signal = classify_sentiment_signal(overall_score)

        except (ValueError, ZeroDivisionError) as error:
            return self._failed(budget, str(error))

        output = self._build_output(
            symbol=symbol,
            average_sentiment=average_sentiment,
            sentiment_classification=sentiment_classification,
            sentiment_strength=sentiment_strength,
            strength_classification=strength_classification,
            sentiment_trend=sentiment_trend,
            overall_score=overall_score,
            sentiment_signal=sentiment_signal,
        )

        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=required_budget,
            status=AgentStatus.COMPLETED,
            output=output,
        )

    def _failed(self, budget: int, reason: str) -> AgentState:
        return AgentState(
            agent_name=self.name,
            reliability=self.reliability,
            allocated_budget=budget,
            used_budget=0,
            status=AgentStatus.FAILED,
            failure_reason=reason,
        )

    def _get_preferred_symbol(
        self,
        query: str,
        available_symbols=None,
    ) -> str | None:
        if self.task_requirement and self.task_requirement.symbols:
            requested = [
                str(symbol).upper()
                for symbol in self.task_requirement.symbols
            ]

            if available_symbols is None:
                return requested[0]

            available_map = {
                str(symbol).upper(): str(symbol)
                for symbol in available_symbols
            }

            for symbol in requested:
                if symbol in available_map:
                    return available_map[symbol]

        return self._find_symbol_in_query(
            query,
            available_symbols,
        )

    @staticmethod
    def _find_symbol_in_query(
        query: str,
        available_symbols=None,
    ) -> str | None:
        if available_symbols is None:
            available_symbols = [
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

        import re

        for symbol in available_symbols:
            normalized = str(symbol).upper()

            if re.search(
                rf"\b{re.escape(normalized)}\b",
                query.upper(),
            ):
                return normalized

        return None

    @staticmethod
    def _build_output(
        symbol: str,
        average_sentiment: float,
        sentiment_classification: str,
        sentiment_strength: float,
        strength_classification: str,
        sentiment_trend: str,
        overall_score: float,
        sentiment_signal: str,
    ) -> str:
        return (
            f"Sentiment Analysis Assessment for {symbol}\n\n"
            f"Overall Assessment: {sentiment_signal}\n\n"
            f"Average sentiment score: {average_sentiment:.4f}\n"
            f"Sentiment classification: {sentiment_classification}\n"
            f"Sentiment strength: {sentiment_strength:.4f}\n"
            f"Strength classification: {strength_classification}\n"
            f"Sentiment trend: {sentiment_trend}\n"
            f"Overall sentiment score: {overall_score:.2f}\n\n"
            f"The supplied sentiment data indicates "
            f"{sentiment_classification.lower()} sentiment for {symbol}. "
            f"This conclusion depends on the quality, recency and coverage "
            "of the supplied sentiment observations. It does not guarantee "
            "future market performance."
        )