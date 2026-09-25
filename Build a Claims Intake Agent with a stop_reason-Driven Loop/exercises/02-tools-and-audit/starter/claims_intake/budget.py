import time
from dataclasses import dataclass


class BudgetExceeded(Exception):
    pass


@dataclass
class Budget:
    max_input_tokens: int
    max_wall_clock_s: float
    _start: float = 0.0
    input_tokens_used: int = 0

    def __post_init__(self) -> None:
        self._start = time.monotonic()

    def record_input_tokens(self, n: int) -> None:
        self.input_tokens_used += n

    def check(self) -> None:
        if self.input_tokens_used > self.max_input_tokens:
            raise BudgetExceeded(
                f"input_tokens_used={self.input_tokens_used} exceeded "
                f"max_input_tokens={self.max_input_tokens}"
            )
        elapsed = time.monotonic() - self._start
        if elapsed > self.max_wall_clock_s:
            raise BudgetExceeded(
                f"elapsed={elapsed:.1f}s exceeded max_wall_clock_s={self.max_wall_clock_s}"
            )
