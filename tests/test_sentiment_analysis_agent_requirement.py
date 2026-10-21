import pandas as pd

from app.agents.sentiment_analysis_agent import (
    SentimentAnalysisAgent,
)
from app.models.schemas import AgentStatus, TaskRequirement


def create_sentiment_data():
    return pd.DataFrame(
        {
            "date": pd.date_range(
                "2026-01-01",
                periods=10,
            ),
            "symbol": ["TCS"] * 10,
            "sentiment_score": [
                0.10,
                0.15,
                0.20,
                0.25,
                0.30,
                0.35,
                0.40,
                0.45,
                0.50,
                0.55,
            ],
        }
    )


def test_sentiment_agent_uses_task_requirement_symbol():
    agent = SentimentAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "sentiment_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        sentiment_data=create_sentiment_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.agent_name == "Sentiment Analysis Agent"
    assert result.output is not None
    assert "TCS" in result.output


def test_sentiment_agent_prefers_structured_symbol():
    agent = SentimentAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected stock",
        required_capabilities=[
            "sentiment_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected stock",
        budget=600,
        sentiment_data=create_sentiment_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert (
        "Sentiment Analysis Assessment for TCS"
        in result.output
    )


def test_sentiment_agent_falls_back_to_query_symbol():
    agent = SentimentAnalysisAgent()

    result = agent.execute(
        query="Analyze TCS sentiment",
        budget=600,
        sentiment_data=create_sentiment_data(),
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert "TCS" in result.output


def test_sentiment_agent_uses_matching_structured_symbol():
    agent = SentimentAnalysisAgent()

    sentiment_data = create_sentiment_data()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "sentiment_analysis"
        ],
        symbols=["TCS"],
    )

    agent.set_task_requirement(requirement)

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        sentiment_data=sentiment_data,
    )

    assert result.status == AgentStatus.COMPLETED
    assert result.output is not None
    assert (
        "Sentiment Analysis Assessment for TCS"
        in result.output
    )


def test_sentiment_agent_rejects_unavailable_structured_symbol():
    agent = SentimentAnalysisAgent()

    requirement = TaskRequirement(
        query="Analyze the selected company",
        required_capabilities=[
            "sentiment_analysis"
        ],
        symbols=["INFY"],
    )

    agent.set_task_requirement(requirement)

    sentiment_data = create_sentiment_data()

    result = agent.execute(
        query="Analyze the selected company",
        budget=600,
        sentiment_data=sentiment_data,
    )

    assert result.status == AgentStatus.FAILED
    assert (
        result.failure_reason
        == "No supported symbol found in query."
    )