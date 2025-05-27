import datetime
import os

import jwt
import pytest

from src.core._shared.infra.auth.jwt_service import JWTService

JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")


@pytest.fixture
def valid_payload():
    return {"username": "itpzzi", "role": "admin"}


@pytest.fixture
def jwt_service():
    return JWTService()


class TestJWTService:
    def test_service_start_with_private_and_public_keys(self, jwt_service):
        assert JWT_PRIVATE_KEY == jwt_service.private_key
        assert JWT_PUBLIC_KEY == jwt_service.public_key
        assert "RS256" == jwt_service.algorithm

    def test_generate_token(self, valid_payload, jwt_service):
        token = jwt_service.generate_token(valid_payload, 60)

        decoded_token = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=["RS256"])

        assert isinstance(token, str)
        assert "exp" in decoded_token
        assert "username" in decoded_token
        assert "role" in decoded_token
        assert (
            decoded_token["exp"]
            > datetime.datetime.now(datetime.timezone.utc).timestamp()
        )

    def test_decode_token(self, valid_payload, jwt_service):
        token = jwt.encode(valid_payload, JWT_PRIVATE_KEY, algorithm="RS256")

        decoded_token = jwt_service.decode_token(token)

        assert isinstance(decoded_token, dict)
        assert "username" in decoded_token
        assert "role" in decoded_token
        assert decoded_token["username"] == valid_payload["username"]
        assert decoded_token["role"] == valid_payload["role"]
