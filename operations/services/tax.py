from collections.abc import Iterable

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from operations.models.tax import Bracket, Tax
from operations.schemas.tax import TaxCreateSchema


class TaxNotFoundError(Exception):
    pass


class TaxAlreadyExistsError(Exception):
    pass


class TaxService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(self, query: str, offset: int, limit: int, order_by: Iterable[str]) -> list[Tax]:
        return (
            self._db.query(Tax)
            .where(Tax.name.ilike(f"%{query}%"))
            .order_by(*[text(field) for field in order_by])
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, tax_id: int) -> Tax:
        tax = self._db.query(Tax).filter(Tax.id == tax_id).first()

        if tax is None:
            message = f"Tax with id {tax_id} not found"
            raise TaxNotFoundError(message)

        return tax

    def create(self, schema: TaxCreateSchema) -> Tax:
        existing_tax = self._db.query(Tax).filter(Tax.name == schema.name).first()

        if existing_tax is not None:
            message = f"Tax with name {schema.name} already exists"
            raise TaxAlreadyExistsError(message)

        tax = Tax(
            name=schema.name,
            rounding_method=schema.rounding_method,
            rounding_to_nearest=schema.rounding_to_nearest,
        )

        self._db.add(tax)

        for b in schema.brackets:
            bracket = Bracket(
                tax_id=tax.id,
                min=b.min,
                max=b.max,
                rate=b.rate,
            )

            self._db.add(bracket)

        self._db.commit()
        self._db.refresh(tax)

        return tax

    def delete(self, tax_id: int) -> None:
        tax = self.get_by_id(tax_id)
        self._db.delete(tax)
        self._db.commit()
