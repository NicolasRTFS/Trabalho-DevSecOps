from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models import Author, Book, Category, Loan, LoanStatus, User, UserRole


def _seed_user(
    db: Session,
    *,
    email: str,
    legacy_email: str,
    name: str,
    password: str,
    role: UserRole,
) -> User:
    user = db.scalar(select(User).where(User.email == email))
    legacy_user = db.scalar(select(User).where(User.email == legacy_email))
    if user is None and legacy_user is not None:
        user = legacy_user
        user.email = email
    if user is None:
        user = User(email=email)
        db.add(user)
    user.name = name
    user.password_hash = hash_password(password)
    user.role = role
    user.is_active = True
    db.flush()
    return user


def _seed_author(db: Session, name: str, biography: str) -> Author:
    author = db.scalar(select(Author).where(Author.name == name))
    if author is None:
        author = Author(name=name, biography=biography)
        db.add(author)
    else:
        author.biography = biography
    db.flush()
    return author


def _seed_category(db: Session, name: str, description: str) -> Category:
    category = db.scalar(select(Category).where(Category.name == name))
    if category is None:
        category = Category(name=name, description=description)
        db.add(category)
    else:
        category.description = description
    db.flush()
    return category


def _seed_book(db: Session, **data) -> Book:
    book = db.scalar(select(Book).where(Book.isbn == data["isbn"]))
    if book is None:
        book = Book(**data)
        db.add(book)
    db.flush()
    return book


def seed_database(db: Session) -> None:
    admin = _seed_user(
        db,
        name="Admin AcervoHub",
        email="admin@example.com",
        legacy_email="admin@acervohub.local",
        password="Admin123!",
        role=UserRole.admin,
    )
    reader = _seed_user(
        db,
        name="Leitor Exemplo",
        email="leitor@example.com",
        legacy_email="leitor@acervohub.local",
        password="Leitor123!",
        role=UserRole.leitor,
    )
    authors = [
        _seed_author(db, "Helena Duarte", "Autora ficticia de obras educacionais."),
        _seed_author(db, "Marcos Valente", "Pesquisador ficticio de cultura digital."),
        _seed_author(db, "Bianca Reis", "Romancista ficticia contemporanea."),
    ]
    categories = [
        _seed_category(db, "Tecnologia", "Livros sobre computacao e inovacao."),
        _seed_category(db, "Literatura", "Ficcao e obras narrativas."),
        _seed_category(db, "Educacao", "Materiais de apoio didatico."),
    ]

    books = [
        _seed_book(db, title="Redes Seguras", isbn="9780000000001", year=2021, description="Fundamentos de seguranca em redes.", author=authors[0], category=categories[0], total_quantity=4, available_quantity=3),
        _seed_book(db, title="Programacao Clara", isbn="9780000000002", year=2020, description="Boas praticas para codigo legivel.", author=authors[1], category=categories[0], total_quantity=3, available_quantity=3),
        _seed_book(db, title="Bibliotecas Vivas", isbn="9780000000003", year=2019, description="Gestao cultural em comunidades.", author=authors[2], category=categories[2], total_quantity=2, available_quantity=1),
        _seed_book(db, title="Algoritmos para Todos", isbn="9780000000004", year=2022, description="Introducao acessivel a algoritmos.", author=authors[1], category=categories[0], total_quantity=5, available_quantity=5),
        _seed_book(db, title="Cadernos da Escola", isbn="9780000000005", year=2018, description="Ensaios sobre aprendizagem.", author=authors[0], category=categories[2], total_quantity=2, available_quantity=2),
        _seed_book(db, title="A Cidade de Papel", isbn="9780000000006", year=2017, description="Romance urbano ficticio.", author=authors[2], category=categories[1], total_quantity=3, available_quantity=3),
        _seed_book(db, title="Dados no Cotidiano", isbn="9780000000007", year=2023, description="Leitura critica de dados.", author=authors[1], category=categories[2], total_quantity=4, available_quantity=4),
        _seed_book(db, title="Noites de Inventario", isbn="9780000000008", year=2016, description="Contos sobre memoria e acervo.", author=authors[2], category=categories[1], total_quantity=1, available_quantity=1),
    ]

    now = datetime.now(timezone.utc)
    if db.scalar(select(Loan).where(Loan.user_id == reader.id)) is None:
        db.add_all(
            [
                Loan(user=reader, book=books[0], loan_date=now - timedelta(days=3), due_date=now + timedelta(days=11), status=LoanStatus.ativo),
                Loan(user=reader, book=books[2], loan_date=now - timedelta(days=20), due_date=now - timedelta(days=6), return_date=now - timedelta(days=2), status=LoanStatus.devolvido),
            ]
        )
    db.commit()
