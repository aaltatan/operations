from decimal import Decimal

from syriantaxes import Rounder, SocialSecurity, calculate_brackets_tax, calculate_fixed_tax

from operations.apps.tax.models import TaxDB

from .schemas import DeductionOutSchema, GrossOutSchema, SalaryOutSchema, TaxOutSchema


class TaxesCalculatorService:
    def _get_salary_schema(
        self,
        gross_salary: Decimal,
        gross_compensation: Decimal,
        brackets_tax: Decimal,
        fixed_tax: Decimal,
        ss_salary: Decimal,
    ) -> SalaryOutSchema:
        return SalaryOutSchema(
            gross=GrossOutSchema(
                salary=gross_salary,
                compensation=gross_compensation,
            ),
            deduction=DeductionOutSchema(
                taxes=TaxOutSchema(brackets=brackets_tax, fixed=fixed_tax),
                social_security=ss_salary,
            ),
        )

    def calculate_gross(  # noqa: PLR0913
        self,
        salary: Decimal,
        compensation: Decimal,
        tax: TaxDB,
        rounder: Rounder,
        ss: SocialSecurity,
        ss_salary: Decimal | None = None,
    ) -> SalaryOutSchema:
        kwargs = {
            "amount": salary,
            "brackets": tax.brackets,
            "min_allowed_salary": tax.min_allowed_salary,
            "rounder": rounder,
        }

        if ss_salary is not None:
            kwargs["ss_obj"] = ss
            kwargs["ss_salary"] = ss_salary

        brackets = calculate_brackets_tax(**kwargs)

        fixed_tax = calculate_fixed_tax(
            amount=compensation, fixed_tax_rate=tax.fixed_tax_rate, rounder=rounder
        )

        schema_kwargs = {
            "gross_salary": salary,
            "gross_compensation": compensation,
            "brackets_tax": brackets,
            "fixed_tax": fixed_tax,
        }

        if ss_salary is not None:
            schema_kwargs["ss_salary"] = ss.calculate_deduction(ss_salary)

        return self._get_salary_schema(**schema_kwargs)
