"""Event Bus Module for Event-Driven Architecture."""
import asyncio
from typing import Callable, Awaitable, Dict, List, Any

EventHandler = Callable[[Any], Awaitable[None]]

class EventBus:
    """Central event bus for the application."""
    def __init__(self):
        """Initialize the event bus with an empty subscriber list."""
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe a handler to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, event_data: Any):
        """Publish an event to all subscribed handlers asynchronously."""
        if event_type in self._subscribers:
            tasks = [handler(event_data) for handler in self._subscribers[event_type]]
            await asyncio.gather(*tasks, return_exceptions=True)

event_bus = EventBus()
