from collections.abc import Iterable

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql import not_, text

from .models import Role, User
from .schemas import UserCreateSchema, UserUpdateSchema


class UserNotFoundError(Exception):
    pass


class UsernameAlreadyExistsError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class PasswordIncorrectError(Exception):
    pass


class UserService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def _hash_password(self, password: str) -> str:
        return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def _set_new_password(self, user: User, new_password: str) -> User:
        user.hash_password = self._hash_password(new_password)
        self._db.commit()
        self._db.refresh(user)
        return user

    def _get_existence_usernames_query(self, usernames: list[str]) -> Query[User]:
        query = self._db.query(User).filter(User.username.in_(usernames))

        if len(usernames) != query.count():
            message = f"Some User with username '{usernames}' not found"
            raise UserNotFoundError(message)

        return query

    def get_all(self, query: str, offset: int, limit: int, order_by: Iterable[str]) -> list[User]:
        return (
            self._db.query(User)
            .where(User.username.ilike(f"%{query}%"))
            .order_by(*[text(field) for field in order_by])
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_uid(self, uid: str) -> User:
        user = self._db.query(User).filter(User.uid == uid).first()

        if user is None:
            message = f"User with uid '{uid}' not found"
            raise UserNotFoundError(message)

        return user

    def get_by_username(self, username: str) -> User:
        user = self._db.query(User).filter(User.username == username).first()

        if user is None:
            message = f"User with username '{username}' not found"
            raise UserNotFoundError(message)

        return user

    def get_by_email(self, email: str) -> User:
        user = self._db.query(User).filter(User.email == email).first()

        if user is None:
            message = f"User with email '{email}' not found"
            raise UserNotFoundError(message)

        return user

    def create(self, schema: UserCreateSchema, password: str) -> User:
        existing_user = self._db.query(User).filter(User.username == schema.username).first()

        if existing_user is not None:
            message = f"User with username '{schema.username}' already exists"
            raise UsernameAlreadyExistsError(message)

        existing_user = self._db.query(User).filter(User.email == schema.email).first()

        if existing_user is not None:
            message = f"User with email '{schema.email}' already exists"
            raise EmailAlreadyExistsError(message)

        user = User(**schema.model_dump(), hash_password=self._hash_password(password))

        self._db.add(user)
        self._db.commit()

        return user

    def update(self, username: str, schema: UserUpdateSchema) -> User:
        user = self.get_by_username(username)

        if schema.username is not None:
            existing_user = self._db.query(User).filter(User.username == schema.username).first()

            if existing_user is not None and existing_user.uid != user.uid:
                message = f"User with username '{schema.username}' already exists"
                raise UsernameAlreadyExistsError(message)

        if schema.email is not None:
            existing_user = self._db.query(User).filter(User.email == schema.email).first()

            if existing_user is not None and existing_user.uid != user.uid:
                message = f"User with email '{schema.email}' already exists"
                raise EmailAlreadyExistsError(message)

        for key, value in schema.model_dump().items():
            if value is not None:
                setattr(user, key, value)

        self._db.commit()
        self._db.refresh(user)

        return user

    def reset_password(self, username: str, new_password: str) -> User:
        user = self.get_by_username(username)
        return self._set_new_password(user, new_password)

    def change_password(self, username: str, old_password: str, new_password: str) -> User:
        user = self.get_by_username(username)

        if not self._verify_password(old_password, user.hash_password):
            message = "Invalid password"
            raise PasswordIncorrectError(message)

        return self._set_new_password(user, new_password)

    def change_role(self, username: str, role: Role) -> User:
        user = self.get_by_username(username)

        if user.role == role:
            return user

        user.role = role

        self._db.commit()
        self._db.refresh(user)

        return user

    def activate(self, username: str) -> User:
        user = self.get_by_username(username)

        if user.is_active:
            return user

        user.is_active = True

        self._db.commit()
        self._db.refresh(user)

        return user

    def activate_bulk(self, usernames: list[str]) -> list[User]:
        query = self._get_existence_usernames_query(usernames)

        activated_users = (
            self._db.query(User).filter(User.is_active, User.username.in_(usernames)).count()
        )

        if activated_users == len(usernames):
            return query.all()

        query.update({User.is_active: True})
        self._db.commit()
        self._db.refresh(query)

        return query.all()

    def deactivate(self, username: str) -> User:
        user = self.get_by_username(username)

        if not user.is_active:
            return user

        user.is_active = False

        self._db.commit()
        self._db.refresh(user)

        return user

    def deactivate_bulk(self, usernames: list[str]) -> list[User]:
        query = self._get_existence_usernames_query(usernames)

        deactivated_users = (
            self._db.query(User).filter(not_(User.is_active), User.username.in_(usernames)).count()
        )

        if deactivated_users == len(usernames):
            return query.all()

        query.update({User.is_active: False})
        self._db.commit()
        self._db.refresh(query)

        return query.all()

    def delete(self, username: str) -> None:
        user = self.get_by_username(username)
        self._db.delete(user)
        self._db.commit()

    def delete_bulk(self, usernames: list[str]) -> None:
        query = self._get_existence_usernames_query(usernames)
        query.delete()
        self._db.commit()

    def empty(self) -> None:
        self._db.query(User).delete()
        self._db.commit()
