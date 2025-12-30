from pydantic import BaseModel, ConfigDict
from syriantaxes import RoundingMethod

from ._types import FourCharString, PositiveDecimal


class SSBaseSchema(BaseModel):
    name: FourCharString
    deduction_rate: PositiveDecimal
    min_allowed_salary: PositiveDecimal
    rounding_to_nearest: PositiveDecimal
    rounding_method: RoundingMethod = RoundingMethod.CEILING

    model_config = ConfigDict(
        json_schema_extra={
            "properties": {
                "name": {
                    "examples": ["نظام التأمينات الجديد"],
                },
                "deduction_rate": {
                    "examples": [0.07],
                },
                "min_allowed_salary": {
                    "examples": [750_000],
                },
                "rounding_to_nearest": {
                    "examples": [1],
                },
                "rounding_method": {
                    "examples": ["CEILING"],
                },
            }
        }
    )


class SSReadSchema(SSBaseSchema):
    id: int


class SSCreateSchema(SSBaseSchema):
    pass


class SSUpdateSchema(BaseModel):
    name: FourCharString | None = None
    deduction_rate: PositiveDecimal | None = None
    min_allowed_salary: PositiveDecimal | None = None
    rounding_method: RoundingMethod | None = None
    rounding_to_nearest: PositiveDecimal | None = None
