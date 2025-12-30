from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from operations.core.config import Config, get_config
from operations.core.db import get_db
from operations.schemas.auth import TokenSchema
from operations.schemas.user import UserReadSchema
from operations.schemas.wrapper import WrapperSchema
from operations.services.auth import CurrentActiveUser, create_access_token
from operations.services.users import authenticate_user

router = APIRouter()


@router.post("/token", response_model=TokenSchema)
def login(
    db: Annotated[Session, Depends(get_db)],
    config: Annotated[Config, Depends(get_config)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=config.access_token_expires_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return TokenSchema(access_token=access_token, token_type=config.token_type)


@router.post("/me", response_model=WrapperSchema[UserReadSchema])
def me(current_user: CurrentActiveUser):
    return WrapperSchema(data=current_user)
