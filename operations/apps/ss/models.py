from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from syriantaxes import RoundingMethod

from operations.core.db import Base

if TYPE_CHECKING:
    from operations.apps.config.models import TaxesCalculatorConfigDB


class SocialSecurityDB(Base):
    __tablename__ = "social_security"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    deduction_rate: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    min_allowed_salary: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False
    )
    rounding_method: Mapped[RoundingMethod] = mapped_column(String(20), nullable=False)
    rounding_to_nearest: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False
    )

    tax_calculator_config: Mapped["TaxesCalculatorConfigDB"] = relationship(
        back_populates="default_ss"
    )

    def __repr__(self) -> str:
        return (
            "<SocialSecurityDB("
            f"id={self.id},"
            f" name={self.name},"
            f" deduction_rate={self.deduction_rate},"
            f" min_allowed_salary={self.min_allowed_salary}"
            f" rounding_method={self.rounding_method},"
            f" rounding_to_nearest={self.rounding_to_nearest}"
            ")>"
        )
