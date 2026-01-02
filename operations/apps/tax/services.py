from collections.abc import Iterable

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .models import BracketDB, TaxDB
from .schemas import TaxCreateSchema, TaxUpdateSchema


class TaxNotFoundError(Exception):
    pass


class TaxAlreadyExistsError(Exception):
    pass


class TaxService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(self, query: str, offset: int, limit: int, order_by: Iterable[str]) -> list[TaxDB]:
        return (
            self._db.query(TaxDB)
            .where(TaxDB.name.ilike(f"%{query}%"))
            .order_by(*[text(field) for field in order_by])
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, tax_id: int) -> TaxDB:
        tax = self._db.query(TaxDB).filter(TaxDB.id == tax_id).first()

        if tax is None:
            message = f"Tax with id '{tax_id}' not found"
            raise TaxNotFoundError(message)

        return tax

    def create(self, schema: TaxCreateSchema) -> TaxDB:
        existing_tax = self._db.query(TaxDB).filter(TaxDB.name == schema.name).first()

        if existing_tax is not None:
            message = f"Tax with name '{schema.name}' already exists"
            raise TaxAlreadyExistsError(message)

        tax_dict = schema.model_dump()
        tax_dict.pop("brackets")

        tax = TaxDB(**tax_dict)

        self._db.add(tax)
        self._db.flush()
        self._db.refresh(tax)

        for bracket in schema.brackets:
            bracket_db = BracketDB(
                tax_id=tax.id, min=bracket.min, max=bracket.max, rate=bracket.rate
            )
            self._db.add(bracket_db)

        self._db.commit()
        self._db.refresh(tax)

        return tax

    def update(self, tax_id: int, schema: TaxUpdateSchema) -> TaxDB:
        tax = self.get_by_id(tax_id)

        tax_dict = schema.model_dump()
        tax_dict.pop("brackets")

        for key, value in tax_dict.items():
            if value is not None:
                setattr(tax, key, value)

        if schema.brackets is not None:
            self._delete_brackets(tax.id)

            for bracket in schema.brackets:
                bracket_db = BracketDB(
                    tax_id=tax.id, min=bracket.min, max=bracket.max, rate=bracket.rate
                )
                self._db.add(bracket_db)

        self._db.commit()
        self._db.refresh(tax)

        return tax

    def _delete_brackets(self, tax_id: int) -> None:
        self._db.query(BracketDB).filter(BracketDB.tax_id == tax_id).delete()

    def delete(self, tax_id: int) -> None:
        tax = self.get_by_id(tax_id)

        self._delete_brackets(tax.id)
        self._db.delete(tax)

        self._db.commit()

    def delete_bulk(self, tax_ids: set[int]) -> None:
        query = self._db.query(TaxDB).filter(TaxDB.id.in_(tax_ids))

        if len(tax_ids) != query.count():
            message = f"Some Tax with id '{tax_ids}' not found"
            raise TaxNotFoundError(message)

        self._db.query(BracketDB).filter(BracketDB.tax_id.in_(tax_ids)).delete()
        query.delete()

        self._db.commit()

    def empty(self) -> None:
        self._db.query(BracketDB).delete()
        self._db.query(TaxDB).delete()
