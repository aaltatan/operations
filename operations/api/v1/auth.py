from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from operations.apps.auth.dependencies import get_current_user
from operations.apps.auth.schemas import TokenSchema
from operations.apps.auth.services import AuthenticationService, InvalidCredentialsError
from operations.apps.users.models import User
from operations.apps.users.schemas import UserReadSchema
from operations.core.config import Config, get_config
from operations.core.db import get_db
from operations.core.schemas import WrapperSchema


def get_user_service(session: Session = Depends(get_db)) -> AuthenticationService:  # noqa: B008
    return AuthenticationService(session)


Service = Annotated[AuthenticationService, Depends(get_user_service)]


router = APIRouter()


@router.post("/token", response_model=TokenSchema)
def login(
    service: Service,
    config: Annotated[Config, Depends(get_config)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    try:
        user = service.authenticate_user(form_data.username, form_data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    access_token = service.create_access_token(
        data={"sub": user.username},
        secret_key=config.secret_key,
        algorithm=config.jwt_algorithm,
        expires_delta=timedelta(minutes=config.access_token_expires_minutes),
    )

    return TokenSchema(access_token=access_token, token_type=config.token_type)


@router.post("/me", response_model=WrapperSchema[UserReadSchema])
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return WrapperSchema(data=current_user)
