from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class AuthorBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    biography: str | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    biography: str | None = None


class AuthorRead(ORMModel, AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None


class CategoryRead(ORMModel, CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class BookBase(BaseModel):
    title: str = Field(min_length=2, max_length=220)
    isbn: str = Field(min_length=10, max_length=32)
    year: int | None = Field(default=None, ge=0, le=2200)
    description: str | None = None
    author_id: int
    category_id: int
    total_quantity: int = Field(ge=0)
    available_quantity: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_quantities(self):
        if self.available_quantity > self.total_quantity:
            raise ValueError("available_quantity cannot exceed total_quantity")
        return self


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=220)
    isbn: str | None = Field(default=None, min_length=10, max_length=32)
    year: int | None = Field(default=None, ge=0, le=2200)
    description: str | None = None
    author_id: int | None = None
    category_id: int | None = None
    total_quantity: int | None = Field(default=None, ge=0)
    available_quantity: int | None = Field(default=None, ge=0)


class BookRead(ORMModel):
    id: int
    title: str
    isbn: str
    year: int | None
    description: str | None
    author_id: int
    category_id: int
    total_quantity: int
    available_quantity: int
    author: AuthorRead
    category: CategoryRead
    created_at: datetime
    updated_at: datetime
