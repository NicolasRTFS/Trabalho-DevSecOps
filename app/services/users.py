from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models import User, UserRole
from app.schemas.users import AdminUserCreate, UserCreate, UserUpdate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, payload: UserCreate | AdminUserCreate, role: UserRole | None = None) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user_role = role or getattr(payload, "role", UserRole.leitor)
    is_active = getattr(payload, "is_active", True)
    user = User(
        name=payload.name,
        email=str(payload.email).lower(),
        password_hash=hash_password(payload.password),
        role=user_role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_not_last_active_admin(db: Session, user: User) -> None:
    if user.role != UserRole.admin or not user.is_active:
        return
    active_admins = db.scalar(
        select(func.count()).select_from(User).where(User.role == UserRole.admin, User.is_active.is_(True))
    )
    if active_admins <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify the last active admin")


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and str(data["email"]).lower() != user.email:
        if get_user_by_email(db, str(data["email"])):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user.email = str(data["email"]).lower()
    if "name" in data:
        user.name = data["name"]
    if "password" in data:
        user.password_hash = hash_password(data["password"])
    if "is_active" in data:
        if data["is_active"] is False:
            ensure_not_last_active_admin(db, user)
        user.is_active = data["is_active"]
    db.commit()
    db.refresh(user)
    return user
