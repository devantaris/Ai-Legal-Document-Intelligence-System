import uuid

import pytest

from app.core.security import (
    CredentialsError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
import uuid


def test_password_hash_roundtrip():
    h = hash_password("hunter22")
    assert h != "hunter22"
    assert verify_password(h, "hunter22")
    assert not verify_password(h, "wrong")


def test_access_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    assert decode_token(token, "access") == user_id
    with pytest.raises(CredentialsError):
        decode_token(token, "refresh")


def test_refresh_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id)
    assert decode_token(token, "refresh") == user_id
    with pytest.raises(CredentialsError):
        decode_token(token, "access")


def test_expired_token_rejected(monkeypatch):
    import app.core.security as sec

    monkeypatch.setattr(sec.settings, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    token = create_access_token(uuid.uuid4())
    with pytest.raises(CredentialsError):
        decode_token(token, "access")


def test_garbage_token_rejected():
    with pytest.raises(CredentialsError):
        decode_token("not.a.token", "access")
