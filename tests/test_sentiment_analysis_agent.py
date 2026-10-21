import pandas as pd

from app.agents.sentiment_analysis_agent import (
    SentimentAnalysisAgent,
)
from app.models.schemas import AgentStatus


def create_sentiment_data():
    return pd.DataFrame(
        {
            "date": pd.date_range(
                start="2025-01-01",
                periods=6,
                freq="D",
            ),
            "symbol": [
                "TCS",
                "TCS",
                "TCS",
                "TCS",
                "TCS",
                "TCS",
            ],
            "sentiment_score": [
                -0.40,
                -0.20,
                0.00,
                0.20,
                0.40,
                0.60,
            ],
        }
    )


def test_sentiment_agent_completes_successfully():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=create_sentiment_data(),
    )

    assert result.status == AgentStatus.COMPLETED


def test_sentiment_agent_returns_correct_agent_name():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=create_sentiment_data(),
    )

    assert result.agent_name == (
        "Sentiment Analysis Agent"
    )


def test_sentiment_agent_detects_positive_sentiment():
    agent = SentimentAnalysisAgent()

    data = create_sentiment_data()

    data["sentiment_score"] = [
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
    ]

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=data,
    )

    assert "Positive" in result.output


def test_sentiment_agent_detects_negative_sentiment():
    agent = SentimentAnalysisAgent()

    data = create_sentiment_data()

    data["sentiment_score"] = [
        -0.80,
        -0.70,
        -0.60,
        -0.50,
        -0.40,
        -0.30,
    ]

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=data,
    )

    assert "Negative" in result.output


def test_sentiment_agent_detects_improving_trend():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=create_sentiment_data(),
    )

    assert "Improving" in result.output


def test_sentiment_agent_rejects_insufficient_budget():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=400,
        sentiment_data=create_sentiment_data(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Insufficient budget."
    )


def test_sentiment_agent_rejects_empty_data():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=pd.DataFrame(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "Sentiment data is empty."
    )


def test_sentiment_agent_rejects_missing_score_column():
    agent = SentimentAnalysisAgent()

    data = pd.DataFrame(
        {
            "symbol": ["TCS"],
        }
    )

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=data,
    )

    assert result.status == AgentStatus.FAILED
    assert "sentiment_score" in (
        result.failure_reason
    )


def test_sentiment_agent_rejects_unknown_symbol():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of AAPL.",
        budget=1000,
        sentiment_data=create_sentiment_data(),
    )

    assert result.status == AgentStatus.FAILED
    assert result.failure_reason == (
        "No supported symbol found in query."
    )


def test_sentiment_agent_uses_required_budget():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze the sentiment of TCS.",
        budget=1000,
        sentiment_data=create_sentiment_data(),
    )

    assert result.used_budget == 450