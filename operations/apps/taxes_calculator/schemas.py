from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, computed_field


class GrossOutSchema(BaseModel):
    salary: Decimal
    compensation: Decimal

    def get_total(self) -> Decimal:
        return self.salary + self.compensation

    @computed_field
    def total(self) -> Decimal:
        return self.get_total()

    @computed_field
    def compensation_to_total(self) -> Decimal:
        return (self.compensation / self.get_total()).quantize(Decimal("0.01"))


class TaxOutSchema(BaseModel):
    brackets: Decimal
    fixed: Decimal

    def get_total(self) -> Decimal:
        return self.brackets + self.fixed

    @computed_field
    def total(self) -> Decimal:
        return self.get_total()


class DeductionOutSchema(BaseModel):
    taxes: TaxOutSchema
    social_security: Decimal = Field(Decimal(0))

    def get_total(self) -> Decimal:
        return self.taxes.get_total() + self.social_security

    @computed_field
    def total(self) -> Decimal:
        return self.get_total()


class SalaryOutSchema(BaseModel):
    gross: GrossOutSchema
    deduction: DeductionOutSchema

    @computed_field
    def net(self) -> Decimal:
        return self.gross.get_total() - self.deduction.get_total()


class GrossInSchema(BaseModel):
    salary: Annotated[Decimal, Field(gt=0, examples=[1_000_000])]
    compensation: Decimal = Field(Decimal(0), examples=[500_000])

    ss_salary: Decimal | None = None
    tax_id: int | None = None
    ss_id: int | None = None
