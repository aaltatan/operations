from typing import Literal

from pydantic import BaseModel, ConfigDict
from syriantaxes import RoundingMethod

from operations.core.schemas import BaseQueryParams, FourCharString, PositiveDecimal


class SSQueryParams(BaseQueryParams):
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
                    "examples": ["ROUND_CEILING"],
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
