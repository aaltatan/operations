from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator
from syriantaxes import RoundingMethod

from ._types import FourCharString, Percentage, PositiveDecimal


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


class BaseTaxSchema(BaseModel):
    name: FourCharString
    rounding_to_nearest: PositiveDecimal
    rounding_method: RoundingMethod = RoundingMethod.CEILING

    model_config = ConfigDict(
        json_schema_extra={
            "properties": {
                "name": {
                    "examples": ["نظام الضرائب الجديد"],
                },
                "rounding_to_nearest": {
                    "examples": [100],
                },
                "rounding_method": {
                    "examples": ["CEILING"],
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
    brackets: list[BaseBracketSchema] = []


class TaxCreateSchema(BaseTaxSchema):
    brackets: list[BaseBracketSchema]


class TaxUpdateSchema(BaseModel):
    name: FourCharString | None = None
    brackets: list[BaseBracketSchema] | None = None
