from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class Category(str, Enum):
    books = "books"
    electronics = "electronics"
    food = "food"

class ItemBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50, examples=["Keyboard"])]
    price: Annotated[float, Field(gt=0, description="Price in USD, must be greater than 0")]
    category: Category = Category.books
    tags: list[str] = Field(default_factory=list)

class ItemCreate(ItemBase):
    """Body for POST /items"""
    pass

class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class Address(BaseModel):
    street: str
    city: str
    zip_code: Annotated[str, Field(pattern=r"^\d{5}$")]

class UserSignup(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")]
    email: str
    password: Annotated[str, Field(min_length=8)]
    confirm_password: str
    age: Annotated[int, Field(ge=18, le=120)]
    address: Address | None = None

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self

    @field_validator("email")
    @classmethod
    def email_must_have_at(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("invalid email")
        return v.lower()

class UserPublic(BaseModel):
    """Response Model: note there is no password field, so it can never leak"""
    username: str
    email: str
    age: int
    address: Address | None = None

class Order(BaseModel):
    item_id: int
    quantity: Annotated[int, Field(ge=1, le=100)]