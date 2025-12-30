from decimal import Decimal

from pydantic import BaseModel, computed_field


class Gross(BaseModel):
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


class Tax(BaseModel):
    brackets: Decimal
    fixed: Decimal

    def get_total(self) -> Decimal:
        return self.brackets + self.fixed

    @computed_field
    def total(self) -> Decimal:
        return self.get_total()


class Deduction(BaseModel):
    taxes: Tax
    social_security: Decimal

    def get_total(self) -> Decimal:
        return self.taxes.get_total() + self.social_security

    @computed_field
    def total(self) -> Decimal:
        return self.get_total()


class SalarySchema(BaseModel):
    gross: Gross
    deduction: Deduction

    @computed_field
    def net(self) -> Decimal:
        return self.gross.get_total() - self.deduction.get_total()
