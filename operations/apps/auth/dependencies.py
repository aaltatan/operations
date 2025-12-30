from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from operations.apps.users.models import User
from operations.core.config import Config, get_config
from operations.core.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


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

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception

    return user


def get_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_admin_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "admin" or not current_user.is_active:
        raise HTTPException(status_code=400, detail="Admin user required")
    return current_user


def get_staff_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role not in ["admin", "staff"] or not current_user.is_active:
        raise HTTPException(status_code=400, detail="Staff user required")
    return current_user
