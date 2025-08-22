from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.db import get_session
from app.models import User
from app.schemas.user import UserCreate
from app.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/login", tags=["login"])


def get_user_by_email(email: str, session: Session) -> User | None:
    """
    Récupère un utilisateur en base de données à partir de son email.

    Args:
        email (str): L'email de l'utilisateur recherché.
        session (Session): La session de base de données.

    Returns:
        User | None: L'utilisateur correspondant ou None si introuvable.
    """
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    return result.first()

@router.post("/token") 
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Authentifie un utilisateur et génère un access token et un refresh token.

    Args:
        form_data (OAuth2PasswordRequestForm): Formulaire contenant l'email (username) et le mot de passe.
        session (Session): La session de base de données.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas ou si le mot de passe est incorrect.

    Returns:
        dict: Un dictionnaire contenant l'access token et le refresh token.
    """
    user = get_user_by_email(form_data.username, session)
    if not user:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé")
    if not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh-token")
def refresh_access_token(
    refresh_token: str = Body(..., embed=True), session: Session = Depends(get_session)
):
    """
    Rafraîchit un access token à partir d’un refresh token valide.

    Args:
        refresh_token (str): Le refresh token envoyé par l'utilisateur.
        session (Session): La session de base de données.

    Raises:
        HTTPException: Si le token est expiré, invalide, ou si l'utilisateur n'existe pas.

    Returns:
        dict: Un dictionnaire contenant un nouveau access token et son type.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="refresh token expiré ou invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )

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
    """
    Récupère les informations de l'utilisateur actuellement authentifié.

    Args:
        current_user (User): L'utilisateur authentifié, récupéré via le token.

    Returns:
        User: Les informations de l'utilisateur connecté.
    """
    return current_user

@router.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Inscrit un nouvel utilisateur dans la base de données.

    Args:
        user_data (UserCreate): Données fournies par l'utilisateur (nom, email, mot de passe, etc.).
        session (Session): La session de base de données.

    Raises:
        HTTPException: Si l'email est déjà enregistré.

    Returns:
        dict: Un message de succès et les informations de l'utilisateur créé.
    """
    # Check email déjà utilisé
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà enregistré",
        )

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        role="client",
        password_hashed=hash_password(user_data.password),
        address_user=user_data.address_user,
        phone=user_data.phone,
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
            "phone": user.phone,
        },
    }
