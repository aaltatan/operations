# ruff: noqa: B008 ARG001
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from operations.core.auth import get_admin_user, get_staff_user
from operations.core.db import get_db
from operations.schemas.common import BaseQueryParams, WrapperSchema
from operations.schemas.ss import SSCreateSchema, SSReadSchema, SSUpdateSchema
from operations.services.ss import SocialSecurityService, SSAlreadyExistsError, SSNotFoundError

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class QueryParams(BaseQueryParams):
    order_by: list[
        Literal[
            "id ASC",
            "id DESC",
            "name",
            "name ASC",
            "deduction_rate",
            "deduction_rate ASC",
            "min_allowed_salary",
            "min_allowed_salary ASC",
        ]
    ] = ["id ASC"]  # noqa: RUF012


def get_taxes_service(session: Session = Depends(get_db)) -> SocialSecurityService:
    return SocialSecurityService(session)


Service = Annotated[SocialSecurityService, Depends(get_taxes_service)]


@router.get("/", response_model=WrapperSchema[list[SSReadSchema]])
@limiter.limit("1/second")
def get_all(request: Request, service: Service, params: Annotated[QueryParams, Query()]):
    data = service.get_all(params.q, params.offset, params.limit, params.order_by)
    return WrapperSchema(data=data)


@router.post(
    "/",
    response_model=WrapperSchema[SSReadSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_staff_user)],
)
@limiter.limit("5/minute")
def create(request: Request, service: Service, schema: Annotated[SSCreateSchema, Body()]):
    try:
        data = service.create(schema)
        return WrapperSchema(data=data)
    except SSAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/{tax_id}", response_model=WrapperSchema[SSReadSchema])
@limiter.limit("1/second")
def get_by_id(request: Request, service: Service, tax_id: int):
    try:
        data = service.get_by_id(tax_id)
        return WrapperSchema(data=data)
    except SSNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.put(
    "/{tax_id}",
    response_model=WrapperSchema[SSReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_staff_user)],
)
@limiter.limit("5/minute")
def update(
    request: Request, service: Service, tax_id: int, schema: Annotated[SSUpdateSchema, Body()]
):
    try:
        data = service.update(tax_id, schema)
        return WrapperSchema(data=data)
    except SSNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except SSAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete(
    "/{tax_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
)
@limiter.limit("5/minute")
def delete(request: Request, service: Service, tax_id: int):
    try:
        service.delete(tax_id)
    except SSNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
)
@limiter.limit("5/minute")
def delete_bulk(request: Request, service: Service, ss_ids: Annotated[list[int], Body()]):
    try:
        service.delete_bulk(ss_ids)
    except SSNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/empty",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
)
@limiter.limit("5/minute")
def empty(request: Request, service: Service):
    service.empty()
