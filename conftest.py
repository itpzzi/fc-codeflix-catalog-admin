import pytest
from dotenv import load_dotenv

from src.core._shared.infra.auth.jwt_service import JWTService

load_dotenv()

fake_payload = {
    "realm_access": {
        "roles": [
            "offline_access",
            "admin",
            "uma_authorization",
            "default-roles-codeflix",
        ]
    },
    "sub": "user-id",
    "preferred_username": "testuser",
}


@pytest.fixture(scope="session")
def jwt_token():
    service = JWTService()
    return service.generate_token(
        fake_payload,
        expires_in_minutes=9999,
    )


@pytest.fixture(autouse=True)
def patch_jwt_auth(monkeypatch, request):
    if "skip_fake_auth" in request.keywords:
        return

    def fake_auth(*args, **kwargs):
        return {"sub": "fake-id", "realm_access": {"roles": ["admin"]}}

    monkeypatch.setattr(
        "src.core._shared.infra.auth.jwt_service.JWTService.decode_token",
        lambda self, token: fake_auth(),
    )
