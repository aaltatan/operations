import uuid
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    computed_field,
    field_validator,
    model_validator,
)

from operations.core.schemas import BaseQueryParams

from .models import Role
from .validators import validate_password

StringFourChar = Annotated[str, Field(min_length=4, max_length=255)]
Password = Annotated[SecretStr, Field(min_length=8, max_length=255)]
Username = Annotated[str, Field(min_length=4, max_length=255, pattern=r"^[a-zA-Z0-9_]+$")]


class UserQueryParams(BaseQueryParams):
    order_by: list[
        Literal[
            "uid ASC",
            "uid DESC",
            "username ASC",
            "username DESC",
            "email ASC",
            "email DESC",
            "firstname ASC",
            "firstname DESC",
            "lastname ASC",
            "lastname DESC",
            "role ASC",
            "role DESC",
            "created_at ASC",
            "created_at DESC",
            "updated_at ASC",
            "updated_at DESC",
        ]
    ] = ["created_at DESC"]  # noqa: RUF012


class UserBaseSchema(BaseModel):
    email: EmailStr
    username: Username
    firstname: StringFourChar
    lastname: StringFourChar
    role: Role

    model_config = ConfigDict(
        json_schema_extra={
            "properties": {
                "username": {
                    "examples": ["abdullah_altatan"],
                },
                "email": {
                    "examples": ["a.altatan@example.com"],
                },
                "firstname": {
                    "examples": ["Abdullah"],
                },
                "lastname": {
                    "examples": ["Altatan"],
                },
                "role": {
                    "examples": ["admin", "user", "staff"],
                },
                "password": {
                    "examples": ["12345678"],
                },
            }
        }
    )


class UserReadSchema(UserBaseSchema):
    uid: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"


class UserPasswordSchema(BaseModel):
    password: Password

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, secret_value: SecretStr) -> SecretStr:
        validate_password(secret_value.get_secret_value())
        return secret_value


class UserCreateSchema(UserBaseSchema):
    pass


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    username: Username | None = None
    firstname: StringFourChar | None = None
    lastname: StringFourChar | None = None


class UserChangePasswordSchema(BaseModel):
    old_password: Password
    new_password: Password
    confirm_password: Password

    @field_validator("new_password", mode="after")
    @classmethod
    def validate_password(cls, secret_value: SecretStr) -> SecretStr:
        validate_password(secret_value.get_secret_value())
        return secret_value

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        new_password = self.new_password.get_secret_value()
        confirm_password = self.confirm_password.get_secret_value()

        if new_password != confirm_password:
            message = "Passwords do not match"
            raise ValueError(message)

        return self
