from typing import Annotated

import typer

UsernameOpt = Annotated[
    str,
    typer.Option(
        "--username",
        prompt="Username",
    ),
]

EmailOpt = Annotated[
    str,
    typer.Option(
        "--email",
        prompt="Email",
    ),
]

FirstnameOpt = Annotated[
    str,
    typer.Option(
        "--firstname",
        prompt="Firstname",
    ),
]

LastnameOpt = Annotated[
    str,
    typer.Option(
        "--lastname",
        prompt="Lastname",
    ),
]

PasswordOpt = Annotated[
    str,
    typer.Option(
        "--password",
        prompt="Password",
        hide_input=True,
        confirmation_prompt=True,
    ),
]
