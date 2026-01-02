# ruff : noqa: UP045
from decimal import Decimal
from functools import cache
from typing import Any, Optional, Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from syriantaxes import RoundingMethod

from operations.apps.ss.models import SocialSecurityDB
from operations.apps.tax.models import TaxDB
from operations.core.db import Base


class TaxesCalculatorConfigDB(Base):
    __tablename__ = "taxes_calculator_config"

    id: Mapped[int] = mapped_column(primary_key=True)

    default_tax_id: Mapped[Optional[int]] = mapped_column(ForeignKey("taxes.id"), nullable=True)
    default_tax: Mapped[Optional[TaxDB]] = relationship(back_populates="tax_calculator_config")

    tax_rounding_to_nearest: Mapped[Decimal] = mapped_column(default=Decimal(100))
    tax_rounding_method: Mapped[RoundingMethod] = mapped_column(default=RoundingMethod.CEILING)

    default_ss_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("social_security.id"), nullable=True
    )
    default_ss: Mapped[Optional[SocialSecurityDB]] = relationship(
        back_populates="tax_calculator_config"
    )

    ss_rounding_to_nearest: Mapped[Decimal] = mapped_column(default=Decimal(1))
    ss_rounding_method: Mapped[RoundingMethod] = mapped_column(default=RoundingMethod.CEILING)

    @classmethod
    def update(cls, session: Session, **fields: Any) -> Self:
        obj = cls.load(session)

        for key, value in fields.items():
            if hasattr(obj, key) and value is not None:
                setattr(obj, key, value)

        session.commit()
        session.refresh(obj)
        cls.load.cache_clear()

        return obj

    @classmethod
    @cache
    def load(cls, session: Session) -> Self:
        query = session.query(cls)

        if query.count() > 1:
            query.delete()
            obj = cls()
            session.add(obj)
            session.commit()
            return obj

        obj = query.first()

        if obj is None:
            obj = cls()
            session.add(obj)
            session.commit()

        return obj

    def __repr__(self) -> str:
        return "<TaxesCalculatorConfig>"
