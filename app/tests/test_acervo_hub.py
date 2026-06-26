import asyncio

import pytest
from fastapi import HTTPException

from app.auth.dependencies import require_admin
from app.auth.security import create_access_token, verify_password
from app.main import health
from app.models import Book
from app.schemas.catalog import BookCreate, BookUpdate
from app.schemas.users import AdminUserCreate, UserCreate, UserUpdate
from app.services import catalog
from app.services.loans import create_loan, get_loan, return_loan
from app.services.users import create_user, update_user


def test_user_registration(db):
    user = create_user(db, UserCreate(name="Nova Leitora", email="nova@example.com", password="Senha123!"))
    assert user.role == "leitor"
    assert user.password_hash != "Senha123!"


def test_login(db, admin):
    assert verify_password("Admin123!", admin.password_hash)
    token = create_access_token(str(admin.id))
    assert token


def test_list_books(db):
    books = catalog.list_books(db)
    assert len(books) >= 8


def test_admin_creates_book(db, admin):
    asyncio.run(require_admin(admin))
    book = catalog.create_book(
        db,
        BookCreate(
            title="Livro Teste",
            isbn="9781111111111",
            year=2024,
            description="Livro criado em teste.",
            author_id=1,
            category_id=1,
            total_quantity=2,
            available_quantity=2,
        ),
    )
    assert book.isbn == "9781111111111"


def test_admin_edits_book(db, admin):
    asyncio.run(require_admin(admin))
    book = catalog.update_book(db, catalog.get_book(db, 1), BookUpdate(title="Redes Seguras Atualizado"))
    assert book.title == "Redes Seguras Atualizado"


def test_admin_deletes_book(db, admin):
    asyncio.run(require_admin(admin))
    book = catalog.create_book(
        db,
        BookCreate(
            title="Livro Removivel",
            isbn="9781111111112",
            year=2024,
            description="Pode ser removido.",
            author_id=1,
            category_id=1,
            total_quantity=1,
            available_quantity=1,
        ),
    )
    db.delete(book)
    db.commit()
    assert db.get(Book, book.id) is None


def test_reader_cannot_create_book(reader):
    with pytest.raises(HTTPException) as exc:
        asyncio.run(require_admin(reader))
    assert exc.value.status_code == 403


def test_reader_cannot_access_user_management(reader):
    with pytest.raises(HTTPException) as exc:
        asyncio.run(require_admin(reader))
    assert exc.value.status_code == 403


def test_admin_creates_user(db, admin):
    asyncio.run(require_admin(admin))
    user = create_user(
        db,
        AdminUserCreate(
            name="Operador Teste",
            email="operador@example.com",
            password="Senha123!",
            role="leitor",
            is_active=True,
        ),
    )
    assert user.email == "operador@example.com"


def test_admin_edits_user(db, admin, reader):
    asyncio.run(require_admin(admin))
    user = update_user(db, reader, UserUpdate(name="Leitor Alterado"))
    assert user.name == "Leitor Alterado"


def test_admin_deactivates_user(db, admin, reader):
    asyncio.run(require_admin(admin))
    user = update_user(db, reader, UserUpdate(is_active=False))
    assert user.is_active is False


def test_request_loan(db, reader):
    loan = create_loan(db, reader, 2)
    assert loan.status == "ativo"


def test_block_loan_when_unavailable(db, admin, reader):
    asyncio.run(require_admin(admin))
    book = catalog.create_book(
        db,
        BookCreate(
            title="Sem Estoque",
            isbn="9781111111114",
            year=2024,
            description="Livro indisponivel.",
            author_id=1,
            category_id=1,
            total_quantity=0,
            available_quantity=0,
        ),
    )
    with pytest.raises(HTTPException) as exc:
        create_loan(db, reader, book.id)
    assert exc.value.status_code == 400


def test_return_loan(db, reader):
    loan = create_loan(db, reader, 2)
    returned = return_loan(db, get_loan(db, loan.id), reader)
    assert returned.status == "devolvido"


def test_health():
    assert asyncio.run(health())["status"] == "ok"
