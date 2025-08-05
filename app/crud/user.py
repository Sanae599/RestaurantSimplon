from app.models.tables_user import User
from sqlmodel import Session, select
from app.schemas.user_schemas import (
    UserCreate,
    UserPublic,
    UserUpdate,
    PasswordUpdate,
    PasswordReset,
)

def get_one_user_by_id(session: Session, user_id: int):
    user = session.get(User, user_id)
    if not user:
        return None

    return UserPublic.model_validate(user)

