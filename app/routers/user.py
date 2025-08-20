from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from enumerations import Role
from app.db import get_session
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.security import (
    check_admin,
    check_admin_employee,
    check_email_exists,
    get_current_user,
    hash_password,
    check_admin_self,
    check_user_exists
)

router = APIRouter(prefix="/user", tags=["user"])


# Lister tous les utilisateurs
@router.get("/", response_model=list[UserRead])
def lister_les_utilisateurs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    check_admin(current_user)
    utilisateurs = session.exec(select(User)).all()
    return utilisateurs


# Lire un utilisateur par son id
@router.get("/{user_id}", response_model=UserRead)
def lire_un_utilisateur(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    check_admin_employee(current_user)
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur


# Créer un nouvel utilisateur
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def creer_un_utilisateur(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    check_admin(current_user)
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    check_email_exists(existing_user)

    # Création de l'utilisateur
    nouvel_utilisateur = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=Role.CLIENT,
        password_hashed=hash_password(user.password),
        address_user=user.address_user,
        phone=user.phone,
    )
    session.add(nouvel_utilisateur)
    session.commit()
    session.refresh(nouvel_utilisateur)
    return nouvel_utilisateur


# Modifier partiellement un utilisateur (PATCH)
@router.patch("/{user_id}", response_model=UserRead)
def patch_utilisateur(
    user_id: int,
    user: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    check_admin_self(current_user, user_id)
    utilisateur = session.get(User, user_id)

    check_user_exists(utilisateur)
    update_data = user.model_dump(exclude_unset=True)

    if "role" in update_data:
        check_admin(current_user)

    if "password" in update_data:
        plain = update_data.pop("password")
        utilisateur.password_hashed = hash_password(plain)

    for key, value in update_data.items():
        setattr(utilisateur, key, value)
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    return utilisateur


# Supprimer un utilisateur
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_un_utilisateur(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    check_admin_self(current_user, user_id)
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    session.delete(utilisateur)
    session.commit()
