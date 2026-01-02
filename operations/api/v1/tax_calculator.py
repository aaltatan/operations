# ruff: noqa: B008 ARG001
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from syriantaxes import Rounder, SocialSecurity

from operations.apps.auth.dependencies import get_admin_user
from operations.apps.config.models import TaxesCalculatorConfigDB
from operations.apps.config.schemas import (
    TaxesCalculatorConfigReadSchema,
    TaxesCalculatorConfigUpdateSchema,
)
from operations.apps.ss.services import SocialSecurityService, SSNotFoundError
from operations.apps.tax.models import TaxDB
from operations.apps.tax.services import TaxNotFoundError, TaxService
from operations.apps.taxes_calculator.schemas import GrossInSchema, SalaryOutSchema
from operations.apps.taxes_calculator.services import TaxesCalculatorService
from operations.core.db import get_db

from .ss import get_ss_service
from .tax import get_tax_service


def _get_tax_config_db(session: Session = Depends(get_db)) -> TaxesCalculatorConfigDB:
    return TaxesCalculatorConfigDB.load(session)


def _get_tax_rounder(tax_config: TaxesCalculatorConfigDB = Depends(_get_tax_config_db)) -> Rounder:
    return Rounder(
        method=tax_config.tax_rounding_method,
        to_nearest=tax_config.tax_rounding_to_nearest,
    )


def _get_ss_rounder(tax_config: TaxesCalculatorConfigDB = Depends(_get_tax_config_db)) -> Rounder:
    return Rounder(
        method=tax_config.ss_rounding_method,
        to_nearest=tax_config.ss_rounding_to_nearest,
    )


def get_ss(
    ss_service: SocialSecurityService = Depends(get_ss_service),
    tax_config: TaxesCalculatorConfigDB = Depends(_get_tax_config_db),
    ss_rounder: Rounder = Depends(_get_ss_rounder),
    ss_id: Annotated[int, Query()] | None = None,
) -> SocialSecurity:
    if tax_config.default_ss is not None and ss_id is None:
        ss_db_obj = tax_config.default_ss
        return SocialSecurity(
            min_salary=ss_db_obj.min_allowed_salary,
            deduction_rate=ss_db_obj.deduction_rate,
            rounder=ss_rounder,
        )

    if ss_id is not None:
        try:
            ss_db_obj = ss_service.get_by_id(ss_id)
            return SocialSecurity(
                min_salary=ss_db_obj.min_allowed_salary,
                deduction_rate=ss_db_obj.deduction_rate,
                rounder=ss_rounder,
            )
        except SSNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None

    raise HTTPException(status_code=400, detail="No ss id provided and no default ss id set")


def get_tax_db(
    tax_service: TaxService = Depends(get_tax_service),
    tax_config: TaxesCalculatorConfigDB = Depends(_get_tax_config_db),
    tax_id: Annotated[int, Query()] | None = None,
) -> TaxDB:
    if tax_config.default_tax is not None and tax_id is None:
        return tax_config.default_tax

    if tax_id is not None:
        try:
            return tax_service.get_by_id(tax_id)
        except TaxNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None

    raise HTTPException(status_code=400, detail="No tax id provided and no default tax id set")


Service = Annotated[TaxesCalculatorService, Depends(TaxesCalculatorService)]
TaxRounder = Annotated[Rounder, Depends(_get_tax_rounder)]
TaxDBDependency = Annotated[TaxDB, Depends(get_tax_db)]


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/config",
    response_model=TaxesCalculatorConfigReadSchema,
    dependencies=[Depends(get_admin_user)],
    description=(
        """
        Get the TaxesCalculatorConfig.\n
        - Admin user required.\n
        - Limited to 1 request per second.
        """
    ),
)
@limiter.limit("1/second")
def get_taxes_calculator_config(request: Request, session: Annotated[Session, Depends(get_db)]):
    return TaxesCalculatorConfigDB.load(session)


@router.put(
    "/config",
    response_model=TaxesCalculatorConfigReadSchema,
    dependencies=[Depends(get_admin_user)],
    status_code=status.HTTP_202_ACCEPTED,
    description=(
        """
        Get the TaxesCalculatorConfig.\n
        - Admin user required.\n
        """
    ),
)
def update_taxes_calculator_config(
    session: Annotated[Session, Depends(get_db)],
    schema: Annotated[TaxesCalculatorConfigUpdateSchema, Body()],
):
    schema_dict = schema.model_dump()
    return TaxesCalculatorConfigDB.update(session, **schema_dict)


@router.post(
    "/gross",
    response_model=SalaryOutSchema,
    description=(
        """
        Calculate the taxes for a salary.\n
        - Limited to 1 request per second.
        """
    ),
)
@limiter.limit("1/second")
def calculate_gross(  # noqa: PLR0913
    request: Request,
    service: Service,
    tax_db: TaxDBDependency,
    tax_rounder: TaxRounder,
    ss: Annotated[SocialSecurity, Depends(get_ss)],
    schema: Annotated[GrossInSchema, Body()],
):
    try:
        return service.calculate_gross(
            salary=schema.salary,
            compensation=schema.compensation,
            tax=tax_db,
            rounder=tax_rounder,
            ss=ss,
            ss_salary=schema.ss_salary,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
