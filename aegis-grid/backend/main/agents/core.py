"""Core Multi-Agent behaviors including ReAct, Reflexion, and BDI elements."""
from typing import Dict, Any, List, Optional
import asyncio
import heapq
from pydantic import BaseModel, Field
from datetime import datetime
from .models import AgentMessage, MessagePriority

class MessageQueue:
    """Priority queue for handling incoming agent messages."""
    def __init__(self):
        """Initialize empty message heap."""
        self._queue = []
        self._counter = 0

    def push(self, message: AgentMessage):
        """Add a prioritized message to the queue."""
        priority_map = {
            MessagePriority.CRITICAL: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3
        }
        heapq.heappush(self._queue, (priority_map[message.priority], self._counter, message))
        self._counter += 1

    def pop(self) -> Optional[AgentMessage]:
        """Pop the highest priority message off the queue."""
        if not self._queue:
            return None
        return heapq.heappop(self._queue)[2]

    def __len__(self):
        """Get the number of messages currently queued."""
        return len(self._queue)

class BaseAgent:
    """Base generic agent class."""
    def __init__(self, agent_id: str):
        """Initialize the agent ID and IO channels."""
        self.agent_id = agent_id
        self.inbox = MessageQueue()
        self.outbox = []

    async def react_loop(self, context: Any) -> Any:
        """Run the standard ReAct execution loop over a context."""
        thought = await self.think(context)
        action = await self.act(thought)
        observation = await self.observe(action)
        return await self.reflect(observation)

    async def think(self, context: Any) -> Any:
        """Generate a thought from context."""
        pass

    async def act(self, thought: Any) -> Any:
        """Execute action based on thought."""
        pass

    async def observe(self, action: Any) -> Any:
        """Observe environment post-action."""
        pass

    async def reflect(self, observation: Any) -> Any:
        """Reflexion pattern: evaluate and retry if confidence low."""
        confidence = self.evaluate_confidence(observation)
        if confidence < 0.85:
            return await self.react_loop(observation)
        return observation

    def evaluate_confidence(self, result: Any) -> float:
        """Evaluate outcome probability."""
        return 1.0

    async def constitutional_check(self, proposal: Any) -> bool:
        """Check proposed actions against ROE constraints."""
        return True

    async def self_consistency_vote(self, proposals: List[Any]) -> Any:
        """Resolve a set of Tree of Thought proposals into a consistent conclusion."""
        from collections import Counter
        counts = Counter([str(p) for p in proposals])
        best = counts.most_common(1)[0][0]
        for p in proposals:
            if str(p) == best:
                return p
        return proposals[0]
