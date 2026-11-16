"""09-18: Every way data arives in a URL or request metadata"""

from datetime import datetime
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Cookie, Header, Path, Query, Request

from app.schemas import Category

router = APIRouter(prefix="/params", tags=["02 params"])

#09 - path parameter with a type. eg: required type is int, but /params/users/abc -> 422 because it isn't a integer.
@router.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

#10 - ORDER MATTERS: the fixed path must be declared BEFORE the dynamic one.
@router.get("/profiles/me")
def my_profile():
    return {"profile": "current user"}

@router.get("/profiles/{name}")
def profile(name: str):
    return {"profile": name}


##Day 2:
#11 - path param validated with Path(): numeric constraints.
@router.get("/products/{product_id}")
def product(product_id: Annotated[int, Path(ge=1, le=10_000, title="Product ID")]):
    return {"product_id": product_id}

#12 - Enum path param: only listed values are allowed and they will be shown in drop down in the docs.
@router.get("/category/{category}")
def by_category(category: Category):
    return {"category": category, "is_food": category is Category.food}

#13 - path containing slashes using the :path converter
@router.get("/files/{file_path:path}")
def read_path(file_path: str):
    return {"file_path": file_path}

#14 - query params: required, optional, default, bool parsing(?active=yes/true/1/on)
@router.get("/search")
def search(q: str, page: int = 1, active: bool = False, sort: str | None = None):
    return {"q": q, "page": page, "active": active, "sort": sort}

#15 - query validation + alias + deprecation + regex
@router.get("/validate")
def validated(q: Annotated[str | None, Query(min_length=3, max_length=20, pattern = r"^[a-zA-Z ]+$")] = None,
              item_query: Annotated[str | None, Query(alias="item-query")] = None,
              old: Annotated[str | None, Query(deprecated=True)] = None,
              ):
    return { "q": q, "item_query": item_query, "old": old}

#16 - list query param: ?tag=a&tag=b -> ["a", "b"]. Also UUID date parsing.
@router.get("/multi")
def multi(
    tag: Annotated[list[str] | None, Query()] = None,
    request_id: UUID | None = None,
    since: datetime | None = None
):
    return {"tags": tag or [], "request_id": request_id, "since": since}

#17 - headers and cookies. Header "user_agent" maps from "User-Agent" (underscore -> hyphen)
@router.get("/meta")
def metadata(
    user_agent: Annotated[str | None, Header()] = None,
    x_token: Annotated[list[str] | None, Header()] = None,
    session_id: Annotated[str | None, Cookie()] = None,
):
    return {"user_agent": user_agent, "x_token": x_token, "session_id": session_id}

#18 - the raw Request object: client IP, full URL, all query params, method
@router.get("/raw")
def raw(request: Request):
    return {
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else None,
        "query": dict(request.query_params)
    }

