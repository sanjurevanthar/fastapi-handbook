from typing import Annotated, Any
from fastapi import APIRouter, Body, status
from app.schemas import Address, ItemCreate, Order, UserPublic, UserSignup

router = APIRouter(prefix="/bodies", tags=["03 bodies"])


#19 - a Pydantic model parameter = JSON body. Validated before your code runs.
@router.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    total_with_tax = round(item.price * 1.08, 2)
    return {**item.model_dump(), "price_with_tax": total_with_tax}

#20 - body + path + query together. FastAPI decides by type:
@router.put("/items/{item_id}")
def update_item(item_id: int, item: ItemCreate, notify: bool = False):
    return {"item_id": item_id, "item": item, "notify": notify}

