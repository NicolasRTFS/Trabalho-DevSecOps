from datetime import datetime

from pydantic import BaseModel

from app.models import LoanStatus
from app.schemas.catalog import BookRead
from app.schemas.common import ORMModel
from app.schemas.users import UserRead


class LoanCreate(BaseModel):
    book_id: int


class LoanRead(ORMModel):
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    due_date: datetime
    return_date: datetime | None
    status: LoanStatus
    book: BookRead
    user: UserRead
    created_at: datetime
    updated_at: datetime
