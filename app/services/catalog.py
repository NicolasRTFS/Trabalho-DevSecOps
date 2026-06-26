from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Author, Book, Category
from app.schemas.catalog import AuthorCreate, AuthorUpdate, BookCreate, BookUpdate, CategoryCreate, CategoryUpdate


def get_author(db: Session, author_id: int) -> Author:
    author = db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


def ensure_book_relations(db: Session, author_id: int, category_id: int) -> None:
    get_author(db, author_id)
    get_category(db, category_id)


def create_author(db: Session, payload: AuthorCreate) -> Author:
    author = Author(**payload.model_dump())
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


def update_author(db: Session, author: Author, payload: AuthorUpdate) -> Author:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, key, value)
    db.commit()
    db.refresh(author)
    return author


def delete_author(db: Session, author: Author) -> None:
    if author.books:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author has linked books")
    db.delete(author)
    db.commit()


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, payload: CategoryUpdate) -> Category:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    if category.books:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category has linked books")
    db.delete(category)
    db.commit()


def book_query():
    return select(Book).options(joinedload(Book.author), joinedload(Book.category))


def list_books(db: Session, q: str | None = None) -> list[Book]:
    stmt = book_query()
    if q:
        like = f"%{q}%"
        stmt = stmt.join(Book.author).join(Book.category).where(
            or_(Book.title.ilike(like), Book.isbn.ilike(like), Author.name.ilike(like), Category.name.ilike(like))
        )
    return list(db.scalars(stmt).unique())


def get_book(db: Session, book_id: int) -> Book:
    book = db.scalar(book_query().where(Book.id == book_id))
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


def create_book(db: Session, payload: BookCreate) -> Book:
    if db.scalar(select(Book).where(Book.isbn == payload.isbn)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISBN already registered")
    ensure_book_relations(db, payload.author_id, payload.category_id)
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return get_book(db, book.id)


def update_book(db: Session, book: Book, payload: BookUpdate) -> Book:
    data = payload.model_dump(exclude_unset=True)
    if "isbn" in data and data["isbn"] != book.isbn and db.scalar(select(Book).where(Book.isbn == data["isbn"])):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISBN already registered")
    author_id = data.get("author_id", book.author_id)
    category_id = data.get("category_id", book.category_id)
    ensure_book_relations(db, author_id, category_id)
    new_total = data.get("total_quantity", book.total_quantity)
    new_available = data.get("available_quantity", book.available_quantity)
    if new_available > new_total:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid quantities")
    for key, value in data.items():
        setattr(book, key, value)
    db.commit()
    return get_book(db, book.id)
