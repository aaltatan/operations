from typing import Annotated

import typer
from rich.console import Console
from typer_di import Depends, TyperDI

from operations.apps.users.schemas import UserCreateSchema
from operations.apps.users.services import UsernameAlreadyExistsError, UserService

from .dependencies import get_console, get_create_user_schema, get_user_service
from .options import PasswordOpt

app = TyperDI()


@app.command(name="createsuperuser")
def create_superuser(
    schema: Annotated[UserCreateSchema, Depends(get_create_user_schema)],
    password: PasswordOpt,
    service: Annotated[UserService, Depends(get_user_service)],
    console: Annotated[Console, Depends(get_console)],
):
    try:
        user = service.create(schema, password=password)
    except UsernameAlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from None

    console.print(f"[green]User '{user.username}' created successfully[/green]")
