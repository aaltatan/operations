from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator
from syriantaxes import RoundingMethod

from operations.core.schemas import BaseQueryParams, FourCharString, Percentage, PositiveDecimal


class TaxQueryParams(BaseQueryParams):
    order_by: list[Literal["id ASC", "id DESC", "name", "name ASC"]] = ["id ASC"]  # noqa: RUF012


class BaseBracketSchema(BaseModel):
    min: PositiveDecimal
    max: PositiveDecimal
    rate: Percentage

    model_config = ConfigDict(
        json_schema_extra={
            "properties": {
                "min": {
                    "examples": [0, 837_000, 850_000, 1_100_000],
                },
                "max": {
                    "examples": [837_000, 850_000, 1_100_000, 25_000_000],
                },
                "rate": {
                    "examples": [0, 0.11, 0.13, 0.15],
                },
            }
        }
    )

    @model_validator(mode="after")
    def validate_bracket(self) -> Self:
        if self.min >= self.max:
            message = "Min must be less than max"
            raise ValueError(message)

        return self


class BracketReadSchema(BaseBracketSchema):
    pass


class BaseTaxSchema(BaseModel):
    name: FourCharString
    min_allowed_salary: PositiveDecimal
    fixed_tax_rate: Percentage
    compensation_rate: Percentage
    rounding_to_nearest: PositiveDecimal
    rounding_method: RoundingMethod = RoundingMethod.CEILING

    model_config = ConfigDict(
        json_schema_extra={
            "properties": {
                "name": {
                    "examples": ["نظام الضرائب الجديد"],
                },
                "min_allowed_salary": {
                    "examples": [837_000],
                },
                "fixed_tax_rate": {
                    "examples": [0.05],
                },
                "compensation_rate": {
                    "examples": [0.75],
                },
                "rounding_to_nearest": {
                    "examples": [100],
                },
                "rounding_method": {
                    "examples": [RoundingMethod.CEILING],
                },
                "brackets": {
                    "examples": [
                        [
                            {
                                "min": 0,
                                "max": 837_000,
                                "rate": 0,
                            },
                            {
                                "min": 837_000,
                                "max": 850_000,
                                "rate": 0.11,
                            },
                            {
                                "min": 850_000,
                                "max": 1_100_000,
                                "rate": 0.13,
                            },
                            {
                                "min": 1_100_000,
                                "max": 25_000_000,
                                "rate": 0.15,
                            },
                        ],
                    ],
                },
            }
        }
    )


class TaxReadSchema(BaseTaxSchema):
    id: int
    brackets: list[BracketReadSchema] = []


class TaxCreateSchema(BaseTaxSchema):
    brackets: list[BaseBracketSchema]


class TaxUpdateSchema(BaseModel):
    name: FourCharString | None = None
    min_allowed_salary: PositiveDecimal | None = None
    fixed_tax_rate: Percentage | None = None
    compensation_rate: Percentage | None = None
    rounding_method: RoundingMethod | None = None
    rounding_to_nearest: PositiveDecimal | None = None
    brackets: list[BaseBracketSchema] | None = None
