import datetime
import os
from typing import Optional

import jwt

from src.core._shared.infra.auth.abstract_token_service import AbstractTokenService


class JWTService(AbstractTokenService):
    def __init__(self):
        self.private_key = os.getenv("JWT_PRIVATE_KEY")
        self.public_key = os.getenv("JWT_PUBLIC_KEY")
        self.algorithm = "RS256"

    def generate_token(self, payload: dict, expires_in_minutes: Optional[int]):
        payload = payload.copy()
        payload["exp"] = self._generate_expiration_time(expires_in_minutes)
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])

    def _generate_expiration_time(self, expires_in_minutes: int = 60) -> datetime:
        return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=expires_in_minutes
        )
