# ruff: noqa: B008 ARG001
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from operations.core.auth import get_admin_user, get_staff_user
from operations.core.db import get_db
from operations.schemas.common import BaseQueryParams, WrapperSchema
from operations.schemas.tax import TaxCreateSchema, TaxReadSchema
from operations.services.tax import TaxAlreadyExistsError, TaxNotFoundError, TaxService


def get_tax_service(session: Session = Depends(get_db)) -> TaxService:
    return TaxService(session)


Service = Annotated[TaxService, Depends(get_tax_service)]


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class QueryParams(BaseQueryParams):
    order_by: list[
        Literal[
            "id ASC",
            "id DESC",
            "name",
            "name ASC",
        ]
    ] = ["id ASC"]  # noqa: RUF012


@router.get("/", response_model=WrapperSchema[list[TaxReadSchema]])
@limiter.limit("5/minute")
def get_all(request: Request, service: Service, params: Annotated[QueryParams, Query()]):
    data = service.get_all(params.q, params.offset, params.limit, params.order_by)
    return WrapperSchema(data=data)


@router.get("/{tax_id}", response_model=WrapperSchema[TaxReadSchema])
@limiter.limit("1/second")
def get_by_id(request: Request, service: Service, tax_id: int):
    try:
        data = service.get_by_id(tax_id)
        return WrapperSchema(data=data)
    except TaxNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.post(
    "/",
    response_model=WrapperSchema[TaxReadSchema],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def create(request: Request, service: Service, schema: Annotated[TaxCreateSchema, Body()]):
    try:
        data = service.create(schema)
        return WrapperSchema(data=data)
    except TaxAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete(
    "/{tax_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
def delete(request: Request, service: Service, tax_id: int):
    try:
        service.delete(tax_id)
    except TaxNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
