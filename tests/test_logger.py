"""Tests for logger module."""

import logging

import pytest

from logger import (
    CorrelationIdFilter,
    CustomJsonFormatter,
    StructuredLogger,
    clear_correlation_id,
    set_correlation_id,
    setup_logging,
)


class TestCorrelationIdFilter:
    def test_filter_adds_correlation_id(self):
        log_filter = CorrelationIdFilter()
        log_filter.correlation_id = "test-id-123"

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        log_filter.filter(record)
        assert record.correlation_id == "test-id-123"

    def test_filter_uses_default_when_no_correlation_id(self):
        log_filter = CorrelationIdFilter()
        log_filter.correlation_id = None

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        log_filter.filter(record)
        assert record.correlation_id == "no-correlation-id"


class TestSetCorrelationId:
    def test_set_correlation_id_with_provided_value(self):
        correlation_id = set_correlation_id("custom-id")
        assert correlation_id == "custom-id"
        clear_correlation_id()

    def test_set_correlation_id_generates_uuid(self):
        correlation_id = set_correlation_id()
        assert correlation_id is not None
        assert len(correlation_id) > 0
        clear_correlation_id()


class TestClearCorrelationId:
    def test_clear_correlation_id(self):
        set_correlation_id("test-id")
        clear_correlation_id()
        from logger import correlation_filter
        assert correlation_filter.correlation_id is None


class TestStructuredLogger:
    def test_log_request(self, caplog):
        logger = StructuredLogger("test")
        with caplog.at_level(logging.INFO):
            logger.log_request(
                method="GET",
                path="/test",
                status_code=200,
                duration=0.5,
                correlation_id="test-id",
            )
        assert len(caplog.records) >= 1

    def test_log_query(self, caplog):
        logger = StructuredLogger("test")
        with caplog.at_level(logging.DEBUG):
            logger.log_query(
                query="SELECT * FROM users",
                duration=0.1,
                correlation_id="test-id",
            )

    def test_log_error(self, caplog):
        logger = StructuredLogger("test")
        with caplog.at_level(logging.ERROR):
            logger.log_error(
                error=Exception("Test error"),
                context={"key": "value"},
                correlation_id="test-id",
            )

    def test_redact_sensitive_data_password(self):
        logger = StructuredLogger("test")
        text = "password=secret123"
        result = logger._redact_sensitive_data(text)
        assert "secret123" not in result
        assert "password=***" in result

    def test_redact_sensitive_data_token(self):
        logger = StructuredLogger("test")
        text = "token=abc123"
        result = logger._redact_sensitive_data(text)
        assert "abc123" not in result
        assert "token=***" in result

    def test_redact_sensitive_data_api_key(self):
        logger = StructuredLogger("test")
        text = "api_key=secret"
        result = logger._redact_sensitive_data(text)
        assert "secret" not in result
        assert "api_key=***" in result

    def test_redact_sensitive_data_secret(self):
        logger = StructuredLogger("test")
        text = "secret=mysecret"
        result = logger._redact_sensitive_data(text)
        assert "mysecret" not in result
        assert "secret=***" in result

    def test_redact_sensitive_data_no_sensitive_info(self):
        logger = StructuredLogger("test")
        text = "SELECT * FROM users WHERE id = 1"
        result = logger._redact_sensitive_data(text)
        assert result == text


class TestSetupLogging:
    def test_setup_logging_does_not_raise(self):
        try:
            setup_logging("INFO")
        except Exception as e:
            pytest.fail(f"setup_logging raised {e}")
