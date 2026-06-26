from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models import Author, Book, Category
from app.schemas.catalog import (
    AuthorCreate,
    AuthorRead,
    AuthorUpdate,
    BookCreate,
    BookRead,
    BookUpdate,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from app.schemas.common import Message
from app.services import catalog as service

books_router = APIRouter(prefix="/books", tags=["books"])
authors_router = APIRouter(prefix="/authors", tags=["authors"])
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@books_router.get("", response_model=list[BookRead])
async def list_books(q: str | None = Query(default=None), db: Session = Depends(get_db)):
    return service.list_books(db, q)


@books_router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    return service.get_book(db, book_id)


@books_router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    return service.create_book(db, payload)


@books_router.put("/{book_id}", response_model=BookRead, dependencies=[Depends(require_admin)])
async def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    return service.update_book(db, service.get_book(db, book_id), payload)


@books_router.delete("/{book_id}", response_model=Message, dependencies=[Depends(require_admin)])
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = service.get_book(db, book_id)
    db.delete(book)
    db.commit()
    return Message(message="Book deleted")


@authors_router.get("", response_model=list[AuthorRead])
async def list_authors(db: Session = Depends(get_db)):
    return list(db.scalars(select(Author).order_by(Author.name)))


@authors_router.get("/{author_id}", response_model=AuthorRead)
async def get_author(author_id: int, db: Session = Depends(get_db)):
    return service.get_author(db, author_id)


@authors_router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_author(payload: AuthorCreate, db: Session = Depends(get_db)):
    return service.create_author(db, payload)


@authors_router.put("/{author_id}", response_model=AuthorRead, dependencies=[Depends(require_admin)])
async def update_author(author_id: int, payload: AuthorUpdate, db: Session = Depends(get_db)):
    return service.update_author(db, service.get_author(db, author_id), payload)


@authors_router.delete("/{author_id}", response_model=Message, dependencies=[Depends(require_admin)])
async def delete_author(author_id: int, db: Session = Depends(get_db)):
    service.delete_author(db, service.get_author(db, author_id))
    return Message(message="Author deleted")


@categories_router.get("", response_model=list[CategoryRead])
async def list_categories(db: Session = Depends(get_db)):
    return list(db.scalars(select(Category).order_by(Category.name)))


@categories_router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    return service.get_category(db, category_id)


@categories_router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return service.create_category(db, payload)


@categories_router.put("/{category_id}", response_model=CategoryRead, dependencies=[Depends(require_admin)])
async def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    return service.update_category(db, service.get_category(db, category_id), payload)


@categories_router.delete("/{category_id}", response_model=Message, dependencies=[Depends(require_admin)])
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    service.delete_category(db, service.get_category(db, category_id))
    return Message(message="Category deleted")
