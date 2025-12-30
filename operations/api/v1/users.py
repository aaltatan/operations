# ruff: noqa: B008 ARG001
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from pydantic import SecretStr
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from operations.apps.auth.dependencies import get_admin_user, get_user
from operations.apps.users.models import Role
from operations.apps.users.schemas import (
    UserChangePasswordSchema,
    UserCreateSchema,
    UserPasswordSchema,
    UserQueryParams,
    UserReadSchema,
    UserUpdateSchema,
)
from operations.apps.users.services import (
    EmailAlreadyExistsError,
    PasswordIncorrectError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
    UserService,
)
from operations.core.db import get_db
from operations.core.schemas import WrapperSchema


def get_user_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(session)


Service = Annotated[UserService, Depends(get_user_service)]


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/",
    response_model=WrapperSchema[list[UserReadSchema]],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Get all users.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def get_all(request: Request, service: Service, params: Annotated[UserQueryParams, Query()]):
    data = service.get_all(params.q, params.offset, params.limit, params.order_by)
    return WrapperSchema(data=data)


@router.get(
    "/{uid}",
    response_model=WrapperSchema[UserReadSchema],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Get a user by uid.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def get_by_uid(request: Request, service: Service, uid: str):
    try:
        data = service.get_by_uid(uid)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.get(
    "/{username}",
    response_model=WrapperSchema[UserReadSchema],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Get a user by username.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def get_by_username(request: Request, service: Service, username: str):
    try:
        data = service.get_by_username(username)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.post(
    "/",
    response_model=WrapperSchema[UserReadSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Create a new user.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def create(
    request: Request,
    service: Service,
    create_schema: Annotated[UserCreateSchema, Body()],
    password_schema: Annotated[UserPasswordSchema, Body()],
):
    try:
        data = service.create(create_schema, password=password_schema.password.get_secret_value())
        return WrapperSchema(data=data)
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put(
    "/{username}",
    response_model=WrapperSchema[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Update a user.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
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
    dependencies=[Depends(get_user)],
    description=(
        """
        Change a user's password.\n
        - User required.\n
        - Limited to 5 requests per minute.
        """
    ),
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


@router.put(
    "/{username}/reset-password",
    response_model=WrapperSchema[UserReadSchema],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Reset a user's password.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
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
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Change a user's role.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def change_role(request: Request, service: Service, username: str, role: Annotated[Role, Body()]):
    try:
        data = service.change_role(username, role)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put(
    "/{username}/deactivate",
    response_model=WrapperSchema[UserReadSchema],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Deactivate a user.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def deactivate(request: Request, service: Service, username: str):
    try:
        data = service.deactivate(username)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put(
    "/bulk/deactivate",
    response_model=WrapperSchema[list[UserReadSchema]],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Deactivate multiple users.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def deactivate_bulk(request: Request, service: Service, usernames: Annotated[list[str], Body()]):
    try:
        data = service.deactivate_bulk(usernames)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put(
    "/bulk/activate",
    response_model=WrapperSchema[list[UserReadSchema]],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Activate multiple users.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def activate_bulk(request: Request, service: Service, usernames: Annotated[list[str], Body()]):
    try:
        data = service.activate_bulk(usernames)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put(
    "/{username}/activate",
    response_model=WrapperSchema[UserReadSchema],
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Activate a user.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def activate(request: Request, service: Service, username: str):
    try:
        data = service.activate(username)
        return WrapperSchema(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Delete a user.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def delete(request: Request, service: Service, username: str):
    try:
        service.delete(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Delete multiple users.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def delete_bulk(request: Request, service: Service, usernames: Annotated[list[str], Body()]):
    try:
        service.delete_bulk(usernames)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/empty",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Delete all users.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def empty(request: Request, service: Service):
    service.empty()
