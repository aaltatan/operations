from typing import Any, Literal

from pydantic import BaseModel, computed_field


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
