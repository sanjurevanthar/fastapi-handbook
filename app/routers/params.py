"""09-18: Every way data arives in a URL or request metadata"""

from fastapi import APIRouter

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
