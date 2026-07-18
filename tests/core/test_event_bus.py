import pytest
import asyncio
from synapse.core.event_bus import EventBus

@pytest.mark.asyncio
async def test_event_bus_handlers():
    bus = EventBus()
    results = []

    async def async_handler(val: int) -> None:
        await asyncio.sleep(0.01)
        results.append(val * 2)

    def sync_handler(val: int) -> None:
        results.append(val + 1)

    bus.subscribe("test_event", async_handler)
    bus.subscribe("test_event", sync_handler)

    await bus.emit("test_event", 5)

    assert 10 in results
    assert 6 in results
