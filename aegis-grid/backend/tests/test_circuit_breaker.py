import pytest
import asyncio
from main.infrastructure.circuit_breaker import circuit_breaker, CircuitBreakerOpenException

@pytest.mark.asyncio
async def test_circuit_breaker_success():
    @circuit_breaker(failure_threshold=2, recovery_timeout=1)
    async def dummy_call(): return "Success"
    assert await dummy_call() == "Success"

@pytest.mark.asyncio
async def test_circuit_breaker_trip():
    @circuit_breaker(failure_threshold=2, recovery_timeout=1)
    async def failing_call(): raise ValueError("Intentional Fail")
    with pytest.raises(ValueError): await failing_call()
    with pytest.raises(ValueError): await failing_call()
    with pytest.raises(CircuitBreakerOpenException): await failing_call()
