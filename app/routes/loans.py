from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database.session import get_db
from app.models import Loan, LoanStatus, User, UserRole
from app.schemas.loans import LoanCreate, LoanRead
from app.services.loans import create_loan, get_loan, loan_query, return_loan

router = APIRouter(tags=["loans"])


@router.post("/loans", response_model=LoanRead, status_code=201)
async def request_loan(payload: LoanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_loan(db, current_user, payload.book_id)


@router.post("/loans/{loan_id}/return", response_model=LoanRead)
async def return_my_loan(loan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = get_loan(db, loan_id)
    return return_loan(db, loan, current_user, is_admin=current_user.role == UserRole.admin)


@router.get("/me/loans", response_model=list[LoanRead])
async def my_loans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(loan_query().where(Loan.user_id == current_user.id).order_by(Loan.loan_date.desc())).unique())


@router.get("/admin/loans", response_model=list[LoanRead], dependencies=[Depends(require_admin)])
async def admin_loans(
    user_id: int | None = None,
    book_id: int | None = None,
    status: LoanStatus | None = None,
    loan_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = loan_query()
    if user_id:
        stmt = stmt.where(Loan.user_id == user_id)
    if book_id:
        stmt = stmt.where(Loan.book_id == book_id)
    if status:
        stmt = stmt.where(Loan.status == status)
    if loan_date:
        start = datetime.combine(loan_date, time.min, tzinfo=timezone.utc)
        end = datetime.combine(loan_date, time.max, tzinfo=timezone.utc)
        stmt = stmt.where(Loan.loan_date.between(start, end))
    return list(db.scalars(stmt.order_by(Loan.loan_date.desc())).unique())


@router.get("/admin/loans/{loan_id}", response_model=LoanRead, dependencies=[Depends(require_admin)])
async def admin_get_loan(loan_id: int, db: Session = Depends(get_db)):
    return get_loan(db, loan_id)
