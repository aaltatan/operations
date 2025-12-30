from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

String = Annotated[str, Field(min_length=4, max_length=255)]
PositiveDecimal = Annotated[Decimal, Field(gt=0)]


class SSBaseSchema(BaseModel):
    name: String
    deduction_rate: PositiveDecimal
    min_allowed_salary: PositiveDecimal


class SSReadSchema(SSBaseSchema):
    id: int


class SSCreateSchema(SSBaseSchema):
    pass


class SSUpdateSchema(BaseModel):
    name: String | None = None
    deduction_rate: PositiveDecimal | None = None
    min_allowed_salary: PositiveDecimal | None = None
