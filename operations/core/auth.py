from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from operations.core.config import Config, get_config
from operations.core.db import get_db
from operations.models.user import User
from operations.services.users import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(tz=UTC) + expires_delta
    else:
        expire = datetime.now(tz=UTC) + timedelta(minutes=15)

    config = get_config()

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.secret_key, algorithm=config.jwt_algorithm)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    config: Annotated[Config, Depends(get_config)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.jwt_algorithm])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception from None

    user = get_user_by_username(username, db)

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_admin_user(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
):
    if current_active_user.role != "admin":
        raise HTTPException(status_code=400, detail="Admin user required")
    return current_active_user


def get_staff_user(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
):
    if current_active_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=400, detail="Staff user required")
    return current_active_user


AdminUser = Annotated[User, Depends(get_admin_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
