from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View

from src.core._shared.infra.auth.jwt_auth_keycloak_service import JWTAuthKeycloakService


class JWTBasedPermission(BasePermission):
    def _get_jwt_token_from_request(self, request: Request) -> str | None:
        return request.headers.get("Authorization", "").replace("Bearer ", "", 1)


class IsAdmin(JWTBasedPermission):
    def has_permission(self, request: Request, _: View) -> bool:
        token = self._get_jwt_token_from_request(request=request)
        return JWTAuthKeycloakService(token).has_role("admin")


class IsAuthenticated(JWTBasedPermission):
    def has_permission(self, request: Request, _: View) -> bool:
        token = self._get_jwt_token_from_request(request=request)
        return JWTAuthKeycloakService(token).is_authenticated()
