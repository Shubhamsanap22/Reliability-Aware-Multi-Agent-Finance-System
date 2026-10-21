from app.agents.investment_agent import InvestmentAgent
from app.agents.risk_agent import RiskAgent
from app.models.schemas import AgentStatus
from app.monitoring.reliability_monitor import ReliabilityMonitor


def test_reliability_increases_after_success():
    agent = InvestmentAgent()
    monitor = ReliabilityMonitor()

    original_reliability = agent.reliability

    new_reliability = monitor.update(
        agent,
        AgentStatus.COMPLETED,
    )

    assert new_reliability == original_reliability + 0.05
    assert agent.reliability == new_reliability


def test_reliability_decreases_after_failure():
    agent = RiskAgent()
    monitor = ReliabilityMonitor()

    original_reliability = agent.reliability

    new_reliability = monitor.update(
        agent,
        AgentStatus.FAILED,
    )

    assert new_reliability == original_reliability - 0.05
    assert agent.reliability == new_reliability


def test_reliability_never_exceeds_one():
    agent = InvestmentAgent()
    agent.reliability = 0.99

    monitor = ReliabilityMonitor()

    monitor.update(
        agent,
        AgentStatus.COMPLETED,
    )

    assert agent.reliability == 1.0


def test_reliability_never_goes_below_zero():
    agent = RiskAgent()
    agent.reliability = 0.01

    monitor = ReliabilityMonitor()

    monitor.update(
        agent,
        AgentStatus.FAILED,
    )

    assert agent.reliability == 0.0