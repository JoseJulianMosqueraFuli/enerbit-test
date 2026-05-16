"""Tests for database module."""

from sqlalchemy.orm import Session

from database import Base, engine, get_db


class TestEngine:
    def test_engine_is_configured(self):
        assert engine is not None

    def test_engine_has_pool_settings(self):
        pool = engine.pool
        assert pool is not None


class TestGetDb:
    def test_get_db_yields_session(self, db_session):
        generator = get_db()
        session = next(generator)
        assert isinstance(session, Session)
        try:
            next(generator)
        except StopIteration:
            pass

    def test_get_db_session_can_execute_query(self, db_session):
        from sqlalchemy import text
        generator = get_db()
        session = next(generator)
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1


class TestBase:
    def test_base_is_declarative(self):
        from sqlalchemy.orm import DeclarativeBase
        assert isinstance(Base, type)
        assert issubclass(Base, DeclarativeBase)
