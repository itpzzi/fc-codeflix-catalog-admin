from src.core._shared.infra.auth.abstract_jwt_auth_service import AbstractJWTAuthService
from src.core._shared.infra.auth.abstract_token_service import AbstractTokenService
from src.core._shared.infra.auth.jwt_service import JWTService


class JWTAuthKeycloakService(AbstractJWTAuthService):
    """
    Serviço responsável por autenticar e autorizar usuários via token JWT compatível com Keycloak.

    Espera tokens JWT assinados com RS256 e contendo a seguinte estrutura mínima de payload:

    {
        "sub": "user-id",
        "preferred_username": "nome_do_usuario",
        "realm_access": {
            "roles": [
                "offline_access",
                "admin",
                "uma_authorization",
                "default-roles-codeflix"
            ]
        },
        "exp": <timestamp UNIX de expiração>
    }

    Dependências:
        - Um serviço de token (JWTService) que implemente AbstractTokenService,
          responsável por decodificar e validar o token via chave pública.

    Métodos:
        - is_authenticated(token: str) -> bool:
            Verifica se o token é válido (decodificável e não expirado).

        - has_role(token: str, role: str) -> bool:
            Verifica se o token contém um papel específico dentro do campo "realm_access.roles".
    """

    def __init__(self, token: str, jwt_service: AbstractTokenService = JWTService()):
        self._token_service = jwt_service
        self._token = token or ""

    def is_authenticated(self) -> bool:
        return bool(self._token_service.decode_token(self._token))

    def has_role(self, role: str) -> bool:
        payload_decoded = self._token_service.decode_token(self._token)
        auth_information = payload_decoded.get("realm_access", {})
        roles = auth_information.get("roles", [])
        return bool(role in roles)
