from sqlmodel import Session, select
from app.models import User 
from fastapi import Depends, HTTPException, status, APIRouter, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.security import hash_password, create_access_token, verify_password, create_refresh_token, SECRET_KEY, ALGORITHM, get_current_user
from app.db import get_session  
from app.schemas.user import UserCreate
from jose import JWTError, jwt

router = APIRouter(prefix="/login", tags=["login"])

def get_user_by_email(email: str, session: Session) -> User | None:
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    return result.first()

@router.post("/token") #tokenaccess
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),session: Session = Depends(get_session)):

    user = get_user_by_email(form_data.username, session)
    if not user:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé")
    if not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh-token") #tokenrefresh
def refresh_access_token(refresh_token: str = Body(..., embed=True), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="refresh token expiré ou invalide",
        headers={"WWW-Authenticate": "Bearer"},)

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception 
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):

    # Vérif email déjà utilisé
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà enregistré"
        )

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        role="client",
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
