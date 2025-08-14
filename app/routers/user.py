from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.schemas.user import UserRead, UserCreate, UserUpdate 
from app.security import hash_password
from app.security import get_current_user
from app.enumerations import Role
from fastapi import HTTPException
from sqlalchemy import select

router = APIRouter(prefix="/user", tags=["user"])

#Lister tous les utilisateurs
@router.get("/", response_model=list[UserRead])
def lister_les_utilisateurs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent lister les utilisateurs."
        )
    utilisateurs = session.exec(select(User)).all()
    return utilisateurs

#Lire un utilisateur par son id
@router.get("/{user_id}", response_model=UserRead)
def lire_un_utilisateur(user_id: int, session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les employées peuvent lister les utilisateurs."
        )
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur

#Créer un nouvel utilisateur
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def creer_un_utilisateur(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  
):
    # Vérif rôle
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent créer un utilisateur."
        )

    # Vérif email déjà utilisé
    existing_user = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà enregistré."
        )

    # Création de l'utilisateur
    nouvel_utilisateur = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        password_hashed=hash_password(user.password),
        address_user=user.address_user,
        phone=user.phone,
    )
    session.add(nouvel_utilisateur)
    session.commit()
    session.refresh(nouvel_utilisateur)
    return nouvel_utilisateur

#Modifier partiellement un utilisateur (PATCH)
@router.patch("/{user_id}", response_model=UserRead)
def patch_utilisateur(user_id: int,
    user: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que votre propre profil."
        )
    utilisateur = session.get(User, user_id)

    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    update_data = user.model_dump(exclude_unset=True)
    
    if "role" in update_data and current_user.role != Role.ADMIN:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seuls les administrateurs peuvent modifier le rôle d’un utilisateur."
    )
        
    if "password" in update_data:
        plain = update_data.pop("password")
        utilisateur.password_hashed = hash_password(plain)
        
    for key, value in update_data.items():
        setattr(utilisateur, key, value)
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    return utilisateur

#Supprimer un utilisateur
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_un_utilisateur(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)  ):
    
    if current_user.id != user_id and current_user.role != Role.ADMIN :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous pouvez supprimer que votre profil."
        )
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    session.delete(utilisateur)
    session.commit()