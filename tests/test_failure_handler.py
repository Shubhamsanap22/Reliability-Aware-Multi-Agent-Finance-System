from app.handling.failure_handler import FailureHandler


def test_retry_allowed_before_limit():
    handler = FailureHandler(max_retries=2)

    assert handler.should_retry(1) is True


def test_retry_stops_at_limit():
    handler = FailureHandler(max_retries=2)

    assert handler.should_retry(2) is False


def test_custom_retry_limit():
    handler = FailureHandler(max_retries=3)

    assert handler.should_retry(1) is True
    assert handler.should_retry(2) is True
    assert handler.should_retry(3) is False


from app.agents.risk_agent import RiskAgent
from app.agents.investment_agent import InvestmentAgent


def test_select_fallback_agent():
    handler = FailureHandler()

    failed_agent = RiskAgent()
    fallback_agent = InvestmentAgent()

    result = handler.select_fallback(
        failed_agent=failed_agent,
        available_agents=[failed_agent, fallback_agent],
    )

    assert result is fallback_agent


def test_no_fallback_available():
    handler = FailureHandler()

    failed_agent = RiskAgent()

    result = handler.select_fallback(
        failed_agent=failed_agent,
        available_agents=[failed_agent],
    )

    assert result is None