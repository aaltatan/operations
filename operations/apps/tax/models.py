from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from syriantaxes import RoundingMethod

from operations.core.db import Base


class Tax(Base):
    __tablename__ = "taxes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    min_allowed_salary: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False
    )
    fixed_tax_rate: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    compensation_rate: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False
    )
    rounding_method: Mapped[RoundingMethod] = mapped_column(String(20), nullable=False)
    rounding_to_nearest: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False
    )

    brackets: Mapped[list["Bracket"]] = relationship("Bracket", back_populates="tax")

    def __repr__(self) -> str:
        return (
            "<Tax("
            f"id={self.id},"
            f" name={self.name},"
            f" min_allowed_salary={self.min_allowed_salary},"
            f" fixed_tax_rate={self.fixed_tax_rate},"
            f" compensation_rate={self.compensation_rate},"
            f" rounding_method={self.rounding_method},"
            f" rounding_to_nearest={self.rounding_to_nearest}"
            ")>"
        )


class Bracket(Base):
    __tablename__ = "brackets"

    id: Mapped[int] = mapped_column(primary_key=True)

    min: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    max: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    rate: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)

    tax_id: Mapped[int] = mapped_column(ForeignKey("taxes.id"), nullable=False)
    tax: Mapped["Tax"] = relationship("Tax", back_populates="brackets")

    def __repr__(self) -> str:
        return f"<Bracket(id={self.id}, min={self.min}, max={self.max}, rate={self.rate})>"
