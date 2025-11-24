from hypothesis import given, settings
from hypothesis import strategies as st

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_token,
)


@settings(max_examples=5, deadline=None)
@given(st.text(min_size=1, max_size=50))
def test_password_hashing_invariant(password: str):
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password(password + "wrong", hashed)


@given(st.uuids())
def test_login_returns_valid_tokens(user_id):
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    access_user_id = verify_token(access_token, "access")
    refresh_user_id = verify_token(refresh_token, "refresh")

    assert access_user_id == user_id
    assert refresh_user_id == user_id


@given(st.text(min_size=1, max_size=100))
def test_invalid_tokens_are_rejected(invalid_token: str):
    result = verify_token(invalid_token, "access")
    assert result is None


@given(st.uuids())
def test_token_type_mismatch_rejected(user_id):
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    assert verify_token(access_token, "refresh") is None
    assert verify_token(refresh_token, "access") is None


@given(st.uuids())
def test_decode_token_returns_payload(user_id):
    token = create_access_token(user_id)
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload
