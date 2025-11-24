from src.core.config import settings


def test_settings_loaded() -> None:
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 15
    assert settings.bcrypt_rounds == 12
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.jwt_secret is not None
    assert str(settings.database_url).startswith("postgresql+asyncpg://")
