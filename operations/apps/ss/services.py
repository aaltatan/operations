from collections.abc import Iterable

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .models import SocialSecurity
from .schemas import SSCreateSchema, SSUpdateSchema


class SSNotFoundError(Exception):
    pass


class SSAlreadyExistsError(Exception):
    pass


class SocialSecurityService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(
        self, query: str, offset: int, limit: int, order_by: Iterable[str]
    ) -> list[SocialSecurity]:
        return (
            self._db.query(SocialSecurity)
            .where(SocialSecurity.name.ilike(f"%{query}%"))
            .order_by(*[text(field) for field in order_by])
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, ss_id: int) -> SocialSecurity:
        tax = self._db.query(SocialSecurity).filter(SocialSecurity.id == ss_id).first()

        if tax is None:
            message = f"Social Security with id '{ss_id}' not found"
            raise SSNotFoundError(message)

        return tax

    def create(self, schema: SSCreateSchema) -> SocialSecurity:
        existing_tax = (
            self._db.query(SocialSecurity).filter(SocialSecurity.name == schema.name).first()
        )

        if existing_tax is not None:
            message = f"Social Security with name '{schema.name}' already exists"
            raise SSAlreadyExistsError(message)

        tax = SocialSecurity(
            name=schema.name,
            deduction_rate=schema.deduction_rate,
            min_allowed_salary=schema.min_allowed_salary,
            rounding_method=schema.rounding_method,
            rounding_to_nearest=schema.rounding_to_nearest,
        )

        self._db.add(tax)
        self._db.commit()

        return tax

    def update(self, ss_id: int, schema: SSUpdateSchema) -> SocialSecurity:
        tax = self.get_by_id(ss_id)

        for key, value in schema.model_dump().items():
            if key == "name" and value is not None:
                existing_tax = (
                    self._db.query(SocialSecurity).filter(SocialSecurity.name == value).first()
                )

                if existing_tax is not None and existing_tax.id != ss_id:
                    message = f"Social Security with name '{value}' already exists"
                    raise SSAlreadyExistsError(message)

            if value is not None:
                setattr(tax, key, value)

        self._db.commit()
        self._db.refresh(tax)

        return tax

    def delete(self, ss_id: int) -> None:
        tax = self.get_by_id(ss_id)
        self._db.delete(tax)
        self._db.commit()

    def delete_bulk(self, ss_ids: set[int]) -> None:
        query = self._db.query(SocialSecurity).filter(SocialSecurity.id.in_(ss_ids))

        if len(ss_ids) != query.count():
            message = f"Some Social Security with id '{ss_ids}' not found"
            raise SSNotFoundError(message)

        query.delete()
        self._db.commit()

    def empty(self) -> None:
        self._db.query(SocialSecurity).delete()
        self._db.commit()
