from src.db.base import Base
from src.db.session import AsyncSessionLocal, engine


def test_base_model_exists() -> None:
    assert Base is not None
    assert hasattr(Base, "metadata")


def test_engine_configured() -> None:
    assert engine is not None
    assert str(engine.url).startswith("postgresql+asyncpg://")


def test_session_factory_configured() -> None:
    assert AsyncSessionLocal is not None
