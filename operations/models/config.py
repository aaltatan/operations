from decimal import Decimal

from sqlalchemy import DECIMAL
from sqlalchemy.orm import Mapped, Session, mapped_column

from operations.core.db import Base


class TaxConfig(Base):
    __tablename__ = "tax_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    min_allowed_salary: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False, default=Decimal(837_000)
    )
    fixed_tax_rate: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False, default=Decimal("0.05")
    )
    compensation_rate: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), nullable=False, default=Decimal("0.75")
    )

    @classmethod
    def get_config(cls, session: Session) -> "TaxConfig":
        obj = session.query(cls).first()

        if obj is None:
            obj = cls()
            session.add(obj)
            session.commit()

        return obj

    def __repr__(self) -> str:
        return (
            "<TaxConfig("
            f"id={self.id},"
            f" min_allowed_salary={self.min_allowed_salary},"
            f" fixed_tax_rate={self.fixed_tax_rate},"
            f" compensation_rate={self.compensation_rate}"
            ")>"
        )
