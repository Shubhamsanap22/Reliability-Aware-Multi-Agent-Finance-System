from app.models.schemas import BudgetState

class BudgetManager:
        """Manages the computational budget for the multi-agent system."""

        def __init__(self, global_budget: int) -> None:
            self.state = BudgetState(
            global_budget=global_budget,
            allocated_budget=0,
            used_budget=0,
            reserved_budget=0,
        )

        
        def allocate(self, amount: int) -> None:
            """Record budget allocated to an agent."""
            if amount < 0:
                raise ValueError("Allocation amount cannot be negative.")
            self.state.allocated_budget += amount

        def record_usage(self, amount:int) -> None:
            """Record the actual computational budget consumed."""
            if amount<0:
                raise ValueError("Usage amount cannot be negative.")

            self.state.used_budget +=amount


        @property

        def remaining_budget(self) ->int:
            """Return the budget that has not actually been consumed."""
            return self.state.global_budget - self.state.used_budget

        def can_afford(self, amount:int) -> bool:
            """chaeck wheteher the remaing budget can cover an amount."""

            if amount < 0:
                raise ValueError("Amount cannot be negative.")

            return amount<= self.remaining_budget
                 


             