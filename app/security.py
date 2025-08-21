import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.db import get_session
from app.enumerations import Role
from app.models import User

load_dotenv()  # lit le fichier .env à la racine du projet

# Récupération des variables d'environnement
SECRET_KEY = os.environ["SECRET_KEY"]  # lève une erreur si manquante
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.

    Args:
        password (str): Le mot de passe en clair.

    Returns:
        str: Le mot de passe hashé.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond à un mot de passe hashé.

    Args:
        plain_password (str): Le mot de passe en clair.
        hashed_password (str): Le mot de passe hashé.

    Returns:
        bool: True si le mot de passe correspond, False sinon.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Crée un JWT pour l'accès avec expiration.

    Args:
        data (dict): Les données à encoder dans le token (ex: {"sub": email}).
        expires_delta (timedelta | None): Durée de validité du token. 
            Si None, la valeur par défaut ACCESS_TOKEN_EXPIRE_MINUTES est utilisée.

    Returns:
        str: Le token JWT encodé.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """
    Crée un JWT de rafraîchissement avec expiration.

    Args:
        data (dict): Les données à encoder dans le token.
        expires_delta (timedelta | None): Durée de validité du token. 
            Si None, la valeur par défaut REFRESH_TOKEN_EXPIRE_DAYS est utilisée.

    Returns:
        str: Le token JWT encodé.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    """
    Récupère l'utilisateur actuel à partir du token JWT.

    Args:
        token (str): Le token JWT fourni via OAuth2.
        session (Session): Session SQLAlchemy/SQLModel.

    Raises:
        HTTPException: Si le token est invalide ou si l'utilisateur n'existe pas.

    Returns:
        User: L'utilisateur authentifié.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'authentification",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # prendre en compte le token access et pas refresh
        if payload.get("type") != "access":
            raise credentials_exception
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user


def check_admin(current_user):
    """
    Vérifie que l'utilisateur est un administrateur.

    Args:
        current_user (User): L'utilisateur à vérifier.

    Raises:
        HTTPException: Si l'utilisateur n'est pas un admin.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'etes pas admin"
        )


def check_admin_employee(current_user):
    """
    Vérifie que l'utilisateur est un administrateur ou un employé.

    Args:
        current_user (User): L'utilisateur à vérifier.

    Raises:
        HTTPException: Si l'utilisateur n'est ni admin ni employé.
    """
    if current_user.role not in [Role.ADMIN, Role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'etes pas admin ou employée",
        )


def check_email_exists(existing_user):
    """
    Vérifie si un email est déjà utilisé.

    Args:
        existing_user (User | None): L'utilisateur trouvé avec l'email.

    Raises:
        HTTPException: Si l'email est déjà enregistré.
    """
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà enregistré.",
        )


def check_admin_self(current_user, user_id):
    """
    Vérifie qu'un utilisateur peut modifier son propre profil ou qu'il est admin.

    Args:
        current_user (User): L'utilisateur actuel.
        user_id (int): L'ID de l'utilisateur à modifier.

    Raises:
        HTTPException: Si l'utilisateur n'est ni admin ni propriétaire du profil.
    """
    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que votre propre profil.",
        )


def check_user_exists(utilisateur):
    """
    Vérifie que l'utilisateur existe.

    Args:
        utilisateur (User | None): L'utilisateur à vérifier.

    Raises:
        HTTPException: Si l'utilisateur n'existe pas.
    """
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")


def check_name_product_exists(existing_product):
    """
    Vérifie si un produit existe déjà par son nom.

    Args:
        existing_product (Product | None): Produit trouvé.

    Raises:
        HTTPException: Si le produit existe déjà.
    """
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Produit déja existant"
        )


def check_product_exists(product):
    """
    Vérifie qu'un produit existe.

    Args:
        product (Product | None): Produit à vérifier.

    Raises:
        HTTPException: Si le produit n'existe pas.
    """
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
