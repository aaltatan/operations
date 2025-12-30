from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from bcrypt import checkpw
from sqlalchemy.orm import Session

from operations.apps.users.models import User


class InvalidCredentialsError(Exception):
    pass


class AuthenticationService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def authenticate_user(self, username: str, password: str) -> User:
        user = self._db.query(User).filter(User.username == username).first()

        if user is None or not self._verify_password(password, user.hash_password):
            message = "Invalid credentials"
            raise InvalidCredentialsError(message)

        return user

    def create_access_token(
        self, data: dict[str, Any], secret_key: str, algorithm: str, expires_delta: timedelta
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=UTC) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)
