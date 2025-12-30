# ruff: noqa: PLC0415
import sys
from pathlib import Path

import typer


def main() -> None:
    path = Path(__file__).parent.parent
    sys.path.insert(0, str(path))

    from operations.cli.users.app import app as user_app

    app = typer.Typer()

    app.add_typer(user_app, name="users")

    app()


if __name__ == "__main__":
    main()
