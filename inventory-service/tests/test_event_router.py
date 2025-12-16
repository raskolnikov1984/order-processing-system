import pytest
import asyncio
from src.inventory_service.events.router import EventRouter


@pytest.mark.anyio
class TestEventRouter:

    @pytest.fixture(autouse=True)
    async def setup_router(self):
        """Reset router antes de cada test de forma segura"""
        self.router = EventRouter()
        yield  # Permite que el test se ejecute
        # Cleanup opcional aquí si es necesario

    async def test_register_and_dispatch_sync_handler(self):
        """Test registro y dispatch de handler síncrono"""

        results = []

        def sync_handler(data: dict):
            results.append(data)

        self.router.register("TestEvent", sync_handler)

        await self.router.dispatch({"event_type": "TestEvent", "data": "test"})

        assert len(results) == 1
        assert results[0]["data"] == "test"

    async def test_register_and_dispatch_async_handler(self):
        """Test registro y dispatch de handler asíncrono"""

        results = []

        async def async_handler(data: dict):
            await asyncio.sleep(0.01)
            results.append(data)

        self.router.register("AsyncEvent", async_handler)

        await self.router.dispatch({"event_type": "AsyncEvent", "value": 42})

        assert len(results) == 1
        assert results[0]["value"] == 42

    async def test_dispatch_isolates_handler_errors(self):
        """Test que errores en un handler no afectan a otros"""

        results = []

        async def bad_handler(data):
            raise ValueError("Error simulado")

        async def good_handler(data):
            results.append("success")

        self.router.register("BadEvent", bad_handler)
        self.router.register("GoodEvent", good_handler)

        await self.router.dispatch({"event_type": "BadEvent"})
        await self.router.dispatch({"event_type": "GoodEvent"})

        # Assert
        assert len(results) == 1
        assert results[0] == "success"

    async def test_dispatch_logs_unknown_event_type(self, caplog):
        """Test que loguea warning para eventos desconocidos"""
        # Act
        await self.router.dispatch({"event_type": "UnknownEvent"})

        # Assert
        assert "No hay handler para event_type" in caplog.text

    async def test_dispatch_logs_error_in_handler(self, caplog):
        """Test que loguea errores en handlers"""

        async def failing_handler(data):
            raise RuntimeError("Handler failed")

        self.router.register("FailEvent", failing_handler)

        await self.router.dispatch({"event_type": "FailEvent"})

        assert "Error procesando FailEvent" in caplog.text
        assert "Handler failed" in caplog.text

    async def test_register_decorator(self):
        """Test el decorator para registrar handlers"""

        @self.router.register_decorator("DecoratedEvent")
        def decorated_handler(data):
            return "decorated"

        assert "DecoratedEvent" in self.router.handlers
        assert self.router.handlers["DecoratedEvent"] == decorated_handler

    async def test_multiples_registrations(self):
        """Test múltiples handlers registrados"""

        event_types = [f"Event{i}" for i in range(5)]
        handler_calls = {event: 0 for event in event_types}

        for event_type in event_types:
            def make_handler(event):
                async def handler(data):
                    handler_calls[event] += 1
                return handler

            self.router.register(event_type, make_handler(event_type))

        for event_type in event_types:
            await self.router.dispatch({"event_type": event_type})

        assert all(count == 1 for count in handler_calls.values())
