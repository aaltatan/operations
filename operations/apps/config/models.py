from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from operations.apps.ss.models import SocialSecurity
from operations.apps.tax.models import Tax
from operations.core.db import Base


class TaxesCalculatorConfig(Base):
    __tablename__ = "taxes_calculator_config"

    id: Mapped[int] = mapped_column(primary_key=True)

    default_tax_id: Mapped[int] = mapped_column(ForeignKey("taxes.id"), nullable=True)
    default_tax: Mapped[Tax] = relationship(Tax, back_populates="config")

    default_ss_id: Mapped[int] = mapped_column(ForeignKey("social_security.id"), nullable=True)
    default_ss: Mapped[SocialSecurity] = relationship(SocialSecurity, back_populates="config")

    @classmethod
    def get_config(cls, session: Session) -> Self:
        obj = session.query(cls).first()

        if obj is None:
            obj = cls()
            session.add(obj)
            session.commit()

        return obj

    def __repr__(self) -> str:
        return (
            "<TaxesCalculatorConfig("
            f"id={self.id},"
            f" default_tax={self.default_tax.name},"
            f" default_ss={self.default_ss.name}"
            ")>"
        )
