from decimal import Decimal
from typing import Annotated

from pydantic import Field

FourCharString = Annotated[str, Field(min_length=4, max_length=255)]
PositiveDecimal = Annotated[Decimal, Field(gt=0)]
Percentage = Annotated[Decimal, Field(gt=0, lt=1)]
