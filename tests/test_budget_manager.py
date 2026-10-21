import pytest

from app.budget.budget_manager import BudgetManager


def test_initial_budget():
    manager = BudgetManager(3000)

    assert manager.state.global_budget == 3000
    assert manager.state.allocated_budget == 0
    assert manager.state.used_budget == 0
    assert manager.remaining_budget == 3000


def test_budget_allocation():
    manager = BudgetManager(3000)

    manager.allocate(900)
    manager.allocate(900)
    manager.allocate(900)

    assert manager.state.allocated_budget == 2700


def test_budget_usage():
    manager = BudgetManager(3000)

    manager.record_usage(600)
    manager.record_usage(400)
    manager.record_usage(300)

    assert manager.state.used_budget == 1300
    assert manager.remaining_budget == 1700


def test_can_afford():
    manager = BudgetManager(3000)

    manager.record_usage(1300)

    assert manager.can_afford(1700)
    assert not manager.can_afford(1701)


def test_negative_values_rejected():
    manager = BudgetManager(3000)

    with pytest.raises(ValueError):
        manager.allocate(-100)

    with pytest.raises(ValueError):
        manager.record_usage(-100)

    with pytest.raises(ValueError):
        manager.can_afford(-100)