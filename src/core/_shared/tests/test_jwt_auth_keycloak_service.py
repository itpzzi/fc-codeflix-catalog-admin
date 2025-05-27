from unittest.mock import Mock

import pytest

from src.core._shared.infra.auth.jwt_auth_keycloak_service import JWTAuthKeycloakService
from src.core._shared.infra.auth.jwt_service import JWTService


@pytest.fixture
def mock_jwt_service():
    return Mock(spec=JWTService)


class TestJWTAuthKeycloakService:
    def test_is_authenticated_valid_token(self, mock_jwt_service):
        mock_jwt_service.decode_token.return_value = {
            "realm_access": {"roles": ["admin"]}
        }

        auth_keycloak_service = JWTAuthKeycloakService(
            token="fake_valid_token", jwt_service=mock_jwt_service
        )

        assert auth_keycloak_service.is_authenticated() is True

    def test_has_role_with_admin_role(self, mock_jwt_service):
        mock_jwt_service.decode_token.return_value = {
            "realm_access": {"roles": ["admin"]}
        }

        auth_keycloak_service = JWTAuthKeycloakService(
            token="fake_valid_token", jwt_service=mock_jwt_service
        )

        assert auth_keycloak_service.has_role("admin") is True

    def test_has_role_without_admin_role(self, mock_jwt_service):
        mock_jwt_service.decode_token.return_value = {
            "realm_access": {"roles": ["another-role"]}
        }

        auth_keycloak_service = JWTAuthKeycloakService(
            token="fake_valid_token", jwt_service=mock_jwt_service
        )

        assert auth_keycloak_service.has_role("admin") is False
