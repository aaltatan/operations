# ruff: noqa: B008 ARG001
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from operations.apps.auth.dependencies import get_admin_user, get_staff_user
from operations.apps.ss.schemas import SSCreateSchema, SSQueryParams, SSReadSchema, SSUpdateSchema
from operations.apps.ss.services import SocialSecurityService, SSAlreadyExistsError, SSNotFoundError
from operations.core.db import get_db
from operations.core.schemas import WrapperSchema

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def get_taxes_service(session: Session = Depends(get_db)) -> SocialSecurityService:
    return SocialSecurityService(session)


Service = Annotated[SocialSecurityService, Depends(get_taxes_service)]


@router.get(
    "/",
    response_model=WrapperSchema[list[SSReadSchema]],
    description=(
        """
        Get all social security records.\n
        - Limited to 1 request per second.
        """
    ),
)
@limiter.limit("1/second")
def get_all(request: Request, service: Service, params: Annotated[SSQueryParams, Query()]):
    data = service.get_all(params.q, params.offset, params.limit, params.order_by)
    return WrapperSchema(data=data)


@router.post(
    "/",
    response_model=WrapperSchema[SSReadSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_staff_user)],
    description=(
        """
        Create a new social security record.\n
        - Staff user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def create(request: Request, service: Service, schema: Annotated[SSCreateSchema, Body()]):
    try:
        data = service.create(schema)
        return WrapperSchema(data=data)
    except SSAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get(
    "/{tax_id}",
    response_model=WrapperSchema[SSReadSchema],
    description=(
        """
        Get a social security record by id.\n
        - Limited to 1 request per second.
        """
    ),
)
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
    description=(
        """
        Update a social security record.\n
        - Staff user required.\n
        - Limited to 5 requests per minute.
        """
    ),
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
    description=(
        """
        Delete a social security record.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
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
    description=(
        """
        Delete multiple social security records.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def delete_bulk(request: Request, service: Service, ss_ids: Annotated[set[int], Body()]):
    try:
        service.delete_bulk(ss_ids)
    except SSNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None


@router.delete(
    "/empty",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Delete all social security records.\n
        - Admin user required.\n
        - Limited to 5 requests per minute.
        """
    ),
)
@limiter.limit("5/minute")
def empty(request: Request, service: Service):
    service.empty()
