import asyncio
from typing import Callable, Any
from functools import wraps
class CircuitBreakerOpenException(Exception): pass
def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0):
    def decorator(func: Callable) -> Callable:
        state = {"failures": 0, "open": False, "last_failure_time": 0.0}
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if state["open"]:
                import time
                if time.time() - state["last_failure_time"] > recovery_timeout:
                    state["open"] = False; state["failures"] = 0
                else: raise CircuitBreakerOpenException(f"Circuit {func.__name__} is OPEN")
            try: result = await func(*args, **kwargs); state["failures"] = 0; return result
            except Exception as e:
                import time
                state["failures"] += 1; state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold: state["open"] = True
                raise e
        return wrapper
    return decorator
