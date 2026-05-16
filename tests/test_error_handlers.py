"""Tests for error handlers, CircuitBreaker, and EventQueue."""

import pytest
from fastapi import Request, status
from fastapi.responses import JSONResponse

from error_handlers import (
    CircuitBreaker,
    DatabaseError,
    EventQueue,
    NotFoundError,
    database_error_handler,
    generic_exception_handler,
    not_found_error_handler,
    sqlalchemy_database_error_handler,
    sqlalchemy_operational_error_handler,
    validation_error_handler,
)


class TestDatabaseError:
    def test_database_error_default_message(self):
        error = DatabaseError()
        assert error.message == "Database error occurred"

    def test_database_error_custom_message(self):
        error = DatabaseError("Custom error")
        assert error.message == "Custom error"


class TestNotFoundError:
    def test_not_found_error_message(self):
        error = NotFoundError("Customer", "123")
        assert error.message == "Customer with id 123 not found"
        assert error.resource == "Customer"
        assert error.identifier == "123"


class TestDatabaseErrorHandler:
    @pytest.mark.asyncio
    async def test_database_error_handler_returns_503(self):
        mock_request = Request(scope={"type": "http", "method": "GET", "path": "/test"})
        exc = DatabaseError("Test error")
        response = await database_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Retry-After" in response.headers


class TestSqlalchemyDatabaseErrorHandler:
    @pytest.mark.asyncio
    async def test_sqlalchemy_database_error_handler_returns_503(self):
        from sqlalchemy.exc import DatabaseError as SQLAlchemyDatabaseError
        from sqlalchemy.dialects import postgresql

        mock_request = Request(scope={"type": "http", "method": "GET", "path": "/test"})
        exc = SQLAlchemyDatabaseError("statement", {"params": ()}, Exception())
        response = await sqlalchemy_database_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestSqlalchemyOperationalErrorHandler:
    @pytest.mark.asyncio
    async def test_operational_error_handler_returns_503(self):
        from sqlalchemy.exc import OperationalError

        mock_request = Request(scope={"type": "http", "method": "GET", "path": "/test"})
        exc = OperationalError("statement", {"params": ()}, Exception())
        response = await sqlalchemy_operational_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestValidationErrorHandler:
    @pytest.mark.asyncio
    async def test_validation_error_handler_returns_400(self):
        from pydantic import ValidationError

        mock_request = Request(scope={"type": "http", "method": "GET", "path": "/test"})
        try:
            from pydantic import BaseModel

            class TestModel(BaseModel):
                name: str

            TestModel()
        except ValidationError as e:
            response = await validation_error_handler(mock_request, e)
            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestNotFoundErrorHandler:
    @pytest.mark.asyncio
    async def test_not_found_error_handler_returns_404(self):
        mock_request = Request(scope={"type": "http", "method": "GET", "path": "/test"})
        exc = NotFoundError("Customer", "123")
        response = await not_found_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["resource"] == "Customer"
        assert data["identifier"] == "123"


class TestGenericExceptionHandler:
    @pytest.mark.asyncio
    async def test_generic_exception_handler_returns_500(self):
        mock_request = Request(scope={"type": "http", "method": "GET", "path": "/test"})
        exc = Exception("Unexpected error")
        response = await generic_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data


class TestCircuitBreaker:
    def test_circuit_breaker_initialization(self):
        cb = CircuitBreaker(failure_threshold=3, timeout=30)
        assert cb.state == "closed"
        assert cb.failure_count == 0
        assert cb.failure_threshold == 3

    def test_circuit_breaker_successful_call(self):
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "closed"

    def test_circuit_breaker_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, timeout=60)

        def failing_func():
            raise Exception("Failure")

        with pytest.raises(Exception):
            cb.call(failing_func)
        with pytest.raises(Exception):
            cb.call(failing_func)

        assert cb.state == "open"

    def test_circuit_breaker_half_open_after_timeout(self):
        import time

        cb = CircuitBreaker(failure_threshold=1, timeout=1)

        def failing_func():
            raise Exception("Failure")

        with pytest.raises(Exception):
            cb.call(failing_func)

        assert cb.state == "open"

        time.sleep(1.1)

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "closed"

    def test_circuit_breaker_raises_when_open(self):
        cb = CircuitBreaker(failure_threshold=1, timeout=60)

        def failing_func():
            raise Exception("Failure")

        with pytest.raises(Exception):
            cb.call(failing_func)

        with pytest.raises(Exception) as exc_info:
            cb.call(lambda: "test")
        assert "Circuit breaker is open" in str(exc_info.value)


class TestEventQueue:
    def test_event_queue_initialization(self):
        eq = EventQueue()
        assert eq.queue == []

    def test_add_event(self):
        eq = EventQueue()
        event = {"id": "123", "data": "test"}
        eq.add_event(event)
        assert len(eq.queue) == 1
        assert eq.queue[0] == event

    def test_get_events(self):
        eq = EventQueue()
        event1 = {"id": "1", "data": "test1"}
        event2 = {"id": "2", "data": "test2"}
        eq.add_event(event1)
        eq.add_event(event2)

        events = eq.get_events()
        assert len(events) == 2
        assert events[0] == event1
        assert events[1] == event2

    def test_get_events_returns_copy(self):
        eq = EventQueue()
        eq.add_event({"id": "1"})
        events = eq.get_events()
        events.clear()
        assert len(eq.queue) == 1

    def test_clear_events(self):
        eq = EventQueue()
        eq.add_event({"id": "1"})
        eq.add_event({"id": "2"})
        eq.clear_events()
        assert len(eq.queue) == 0
