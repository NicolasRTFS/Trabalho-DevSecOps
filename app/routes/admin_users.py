from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models import User
from app.schemas.common import Message
from app.schemas.users import AdminUserCreate, RoleUpdate, UserRead, UserUpdate
from app.services.users import create_user, ensure_not_last_active_admin, update_user

router = APIRouter(prefix="/admin/users", tags=["admin-users"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UserRead])
async def list_users(db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.id)))


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def admin_create_user(payload: AdminUserCreate, db: Session = Depends(get_db)):
    return create_user(db, payload)


@router.put("/{user_id}", response_model=UserRead)
async def admin_update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return update_user(db, user, payload)


@router.patch("/{user_id}/role", response_model=UserRead)
async def change_role(user_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role != payload.role:
        ensure_not_last_active_admin(db, user)
        user.role = payload.role
        db.commit()
        db.refresh(user)
    return user


@router.patch("/{user_id}/activate", response_model=UserRead)
async def activate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/deactivate", response_model=UserRead)
async def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    ensure_not_last_active_admin(db, user)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=Message)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    ensure_not_last_active_admin(db, user)
    db.delete(user)
    db.commit()
    return Message(message="User deleted")
