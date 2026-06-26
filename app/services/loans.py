from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Book, Loan, LoanStatus, User


def loan_query():
    return select(Loan).options(
        joinedload(Loan.book).joinedload(Book.author),
        joinedload(Loan.book).joinedload(Book.category),
        joinedload(Loan.user),
    )


def create_loan(db: Session, user: User, book_id: int) -> Loan:
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.available_quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not available")
    now = datetime.now(timezone.utc)
    loan = Loan(user_id=user.id, book_id=book.id, loan_date=now, due_date=now + timedelta(days=14), status=LoanStatus.ativo)
    book.available_quantity -= 1
    db.add(loan)
    db.commit()
    return get_loan(db, loan.id)


def get_loan(db: Session, loan_id: int) -> Loan:
    loan = db.scalar(loan_query().where(Loan.id == loan_id))
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    due_date = loan.due_date if loan.due_date.tzinfo else loan.due_date.replace(tzinfo=timezone.utc)
    if loan.status == LoanStatus.ativo and due_date < datetime.now(timezone.utc):
        loan.status = LoanStatus.atrasado
        db.commit()
        db.refresh(loan)
    return loan


def return_loan(db: Session, loan: Loan, current_user: User, is_admin: bool = False) -> Loan:
    if not is_admin and loan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot return another user's loan")
    if loan.status == LoanStatus.devolvido:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan already returned")
    loan.status = LoanStatus.devolvido
    loan.return_date = datetime.now(timezone.utc)
    loan.book.available_quantity += 1
    db.commit()
    return get_loan(db, loan.id)
