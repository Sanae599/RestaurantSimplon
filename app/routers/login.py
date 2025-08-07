from sqlmodel import Session, select
from models import User 
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from security import create_access_token, verify_password,get_current_user
from fastapi import Depends
from sqlmodel import Session
from db import get_session  
from fastapi import Body, status
from schemas.user import UserCreate
from security import hash_password

router = APIRouter(prefix="/login", tags=["login"])

def get_user_by_email(email: str, session: Session) -> User | None:
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    return result.first()

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),session: Session = Depends(get_session)):
    user = get_user_by_email(form_data.username, session)
    if not user:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé")
    if not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token}

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        role=user_data.role,
        password_hashed=hash_password(user_data.password),
        address_user=user_data.address_user,
        phone=user_data.phone
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "message": "Utilisateur créé avec succès",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "phone": user.phone
        }
    }
