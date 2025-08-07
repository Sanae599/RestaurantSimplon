from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlmodel import Session, select
from db import get_session
from models import User
from schemas.authentification import Token, TokenUser
from schemas.user import UserRead, UserCreate
from security import verify_password, hash_password
from typing import List

SECRET_KEY = "1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["login"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# user_by_mail
def get_user(email: str, session: Session):
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

# creation jeton JTW
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# test recup user par le token
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou manquant",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
        return TokenUser(email=email, role=role)
    except JWTError:
        raise credentials_exception

# check role
def require_role(allowed_roles: List[str]):
    def role_checker(current_user: TokenUser = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit : rôle insuffisant."
            )
        return current_user
    return role_checker


# Route login 
@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = get_user(email=form_data.username, session=session)
    if not user or not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="mdp ou password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# test get profile route protégé get current user 
@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# test route register
@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    # check si l'utilisateur existe déjà
    existing_user = get_user(email=user_create.email, session=session)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà.",
        )

    # Hash mdp
    hashed_password = hash_password(user_create.password)

    # Création de l'objet User
    new_user = User(
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        email=user_create.email,
        role=user_create.role,
        password_hashed=hashed_password,
        address_user=user_create.address_user,
        phone=user_create.phone,
        created_at=datetime.now(timezone.utc)
    )

    # add en base
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Création du token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
    data={"sub": new_user.email, "role": new_user.role},
    expires_delta=access_token_expires
)

    return {"access_token": access_token, "token_type": "bearer"}