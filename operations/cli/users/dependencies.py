from collections.abc import Generator
from typing import Annotated, Any

import typer
from pydantic import ValidationError
from rich.console import Console
from sqlalchemy.orm import Session
from typer_di import Depends

from operations.apps.users.schemas import UserCreateSchema
from operations.apps.users.services import UserService
from operations.core.db import get_db, init_db

from .options import EmailOpt, FirstnameOpt, LastnameOpt, UsernameOpt


def get_console() -> Console:
    return Console()


def get_user_service(
    _: Annotated[None, Depends(init_db)],
    session: Annotated[Generator[Session, Any, None], Depends(get_db)],
) -> UserService:
    return UserService(next(session))


def get_create_user_schema(
    username: UsernameOpt, email: EmailOpt, firstname: FirstnameOpt, lastname: LastnameOpt
) -> UserCreateSchema:
    try:
        return UserCreateSchema(
            username=username,
            email=email,
            firstname=firstname,
            lastname=lastname,
            role="admin",
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from None
