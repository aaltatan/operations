from decimal import Decimal

from pydantic import BaseModel
from syriantaxes import RoundingMethod

from operations.apps.ss.schemas import SSReadSchema
from operations.apps.tax.schemas import TaxReadSchema


class TaxesCalculatorConfigReadSchema(BaseModel):
    tax_rounding_to_nearest: Decimal
    tax_rounding_method: RoundingMethod

    ss_rounding_to_nearest: Decimal
    ss_rounding_method: RoundingMethod

    default_tax: TaxReadSchema | None = None
    default_ss: SSReadSchema | None = None


class TaxesCalculatorConfigUpdateSchema(BaseModel):
    tax_rounding_to_nearest: Decimal | None = None
    tax_rounding_method: RoundingMethod | None = None

    ss_rounding_to_nearest: Decimal | None = None
    ss_rounding_method: RoundingMethod | None = None

    default_tax_id: int | None = None
    default_ss_id: int | None = None
