from collections.abc import Iterable

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .models import SocialSecurityDB
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
    ) -> list[SocialSecurityDB]:
        return (
            self._db.query(SocialSecurityDB)
            .where(SocialSecurityDB.name.ilike(f"%{query}%"))
            .order_by(*[text(field) for field in order_by])
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, ss_id: int) -> SocialSecurityDB:
        ss = self._db.query(SocialSecurityDB).filter(SocialSecurityDB.id == ss_id).first()

        if ss is None:
            message = f"Social Security with id '{ss_id}' not found"
            raise SSNotFoundError(message)

        return ss

    def create(self, schema: SSCreateSchema) -> SocialSecurityDB:
        existing_ss = (
            self._db.query(SocialSecurityDB).filter(SocialSecurityDB.name == schema.name).first()
        )

        if existing_ss is not None:
            message = f"Social Security with name '{schema.name}' already exists"
            raise SSAlreadyExistsError(message)

        ss = SocialSecurityDB(**schema.model_dump())

        self._db.add(ss)
        self._db.commit()

        return ss

    def update(self, ss_id: int, schema: SSUpdateSchema) -> SocialSecurityDB:
        ss = self.get_by_id(ss_id)

        if schema.name is not None:
            existing_ss = (
                self._db.query(SocialSecurityDB).filter(SocialSecurityDB.name == schema.name).first()
            )

            if existing_ss is not None and existing_ss.id != ss_id:
                message = f"Social Security with name '{schema.name}' already exists"
                raise SSAlreadyExistsError(message)

        for key, value in schema.model_dump().items():
            if value is not None:
                setattr(ss, key, value)

        self._db.commit()
        self._db.refresh(ss)

        return ss

    def delete(self, ss_id: int) -> None:
        ss = self.get_by_id(ss_id)
        self._db.delete(ss)
        self._db.commit()

    def delete_bulk(self, ss_ids: set[int]) -> None:
        query = self._db.query(SocialSecurityDB).filter(SocialSecurityDB.id.in_(ss_ids))

        if len(ss_ids) != query.count():
            message = f"Some Social Security with id '{ss_ids}' not found"
            raise SSNotFoundError(message)

        query.delete()
        self._db.commit()

    def empty(self) -> None:
        self._db.query(SocialSecurityDB).delete()
        self._db.commit()
