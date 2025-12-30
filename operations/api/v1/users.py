# ruff: noqa: B008 ARG001
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from pydantic import SecretStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from operations.core.db import get_db
from operations.models.user import Role
from operations.schemas.query import BaseQueryParams
from operations.schemas.user import (
    UserChangePasswordSchema,
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from operations.schemas.wrapper import WrapperSchema
from operations.services.users import (
    EmailAlreadyExistsError,
    PasswordIncorrectError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


def get_user_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(session)


Service = Annotated[UserService, Depends(get_user_service)]


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class QueryParams(BaseQueryParams):
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


@router.get("/", response_model=WrapperSchema[list[UserReadSchema]])
@limiter.limit("5/minute")
def get_all(request: Request, service: Service, params: Annotated[QueryParams, Query()]):
    data = service.get_all(params.q, params.offset, params.limit, params.order_by)
    return WrapperSchema(data=data)


@router.get("/{uid}", response_model=WrapperSchema[UserReadSchema])
@limiter.limit("5/minute")
def get_by_uid(request: Request, service: Service, uid: str):
    try:
        data = service.get_by_uid(uid)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.get("/{username}", response_model=WrapperSchema[UserReadSchema])
@limiter.limit("5/minute")
def get_by_username(request: Request, service: Service, username: str):
    try:
        data = service.get_by_username(username)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.post("/", response_model=WrapperSchema[UserReadSchema], status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create(request: Request, service: Service, schema: Annotated[UserCreateSchema, Body()]):
    try:
        data = service.create(schema, password=schema.password.get_secret_value())
        return WrapperSchema(data=data)
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put(
    "/{username}",
    response_model=WrapperSchema[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit("5/minute")
def update(
    request: Request, service: Service, username: str, schema: Annotated[UserUpdateSchema, Body()]
):
    try:
        data = service.update(username, schema)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put(
    "/{username}/change-password",
    response_model=WrapperSchema[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit("5/minute")
def change_password(
    request: Request,
    service: Service,
    username: str,
    schema: Annotated[UserChangePasswordSchema, Body()],
):
    try:
        data = service.change_password(
            username, schema.old_password.get_secret_value(), schema.new_password.get_secret_value()
        )
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except PasswordIncorrectError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{username}/reset-password", response_model=WrapperSchema[UserReadSchema])
@limiter.limit("5/minute")
def reset_password(
    request: Request, service: Service, username: str, new_password: Annotated[SecretStr, Body()]
):
    try:
        data = service.reset_password(username, new_password.get_secret_value())
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put(
    "/{username}/change-role",
    response_model=WrapperSchema[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit("5/minute")
def change_role(request: Request, service: Service, username: str, role: Annotated[Role, Body()]):
    try:
        data = service.change_role(username, role)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put("/{username}/deactivate", response_model=WrapperSchema[UserReadSchema])
@limiter.limit("5/minute")
def deactivate(request: Request, service: Service, username: str):
    try:
        data = service.deactivate(username)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put("/bulk/deactivate", response_model=WrapperSchema[list[UserReadSchema]])
@limiter.limit("5/minute")
def deactivate_bulk(request: Request, service: Service, usernames: Annotated[list[str], Body()]):
    try:
        data = service.deactivate_bulk(usernames)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put("/bulk/activate", response_model=WrapperSchema[list[UserReadSchema]])
@limiter.limit("5/minute")
def activate_bulk(request: Request, service: Service, usernames: Annotated[list[str], Body()]):
    try:
        data = service.activate_bulk(usernames)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put("/{username}/activate", response_model=WrapperSchema[UserReadSchema])
@limiter.limit("5/minute")
def activate(request: Request, service: Service, username: str):
    try:
        data = service.activate(username)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete(request: Request, service: Service, username: str):
    try:
        service.delete(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete_bulk(request: Request, service: Service, usernames: Annotated[list[str], Body()]):
    try:
        service.delete_bulk(usernames)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete("/empty", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def empty(request: Request, service: Service):
    service.empty()
