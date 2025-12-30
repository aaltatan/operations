from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, computed_field

FourCharString = Annotated[str, Field(min_length=4, max_length=255)]
PositiveDecimal = Annotated[Decimal, Field(ge=0)]
Percentage = Annotated[Decimal, Field(ge=0, le=1)]


class BaseQueryParams(BaseModel):
    q: str = ""
    offset: int = 0
    limit: int = 10


class WrapperSchema[T](BaseModel):
    data: T

    @property
    def kind(self) -> Literal["array", "object"]:
        return "array" if isinstance(self.data, list) else "object"

    @property
    def length(self) -> int:
        return len(self.data) if isinstance(self.data, list) else 1

    @computed_field
    def meta(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "length": self.length,
        }
