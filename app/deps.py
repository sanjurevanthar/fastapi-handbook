"""Reusable dependencies, FastAPI calls these for you and inject the results"""

from typing import Annotated, TypedDict
from fastapi import Depends, Query

class PaginationParams(TypedDict):
    skip: int
    limit: int

def pagination(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> PaginationParams:
    return {"skip": skip, "limit": limit}

Pagination = Annotated[PaginationParams, Depends(pagination)]

class CommonFilters:
    def __init__(
        self,
        q: str | None = None,
        min_price: Annotated[float | None, Query(ge=0)] = None,
    ):
        self.q = q
        self.min_price = min_price

Filters = Annotated[CommonFilters, Depends()]