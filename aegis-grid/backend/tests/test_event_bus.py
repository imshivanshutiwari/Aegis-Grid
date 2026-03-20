import pytest
import asyncio
from main.core.event_bus import event_bus
@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    test_result = []
    async def test_handler(data): test_result.append(data)
    event_bus.subscribe("test_event", test_handler)
    await event_bus.publish("test_event", {"key": "value"})
    assert len(test_result) == 1
    assert test_result[0] == {"key": "value"}
