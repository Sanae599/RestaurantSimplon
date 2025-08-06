from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db import get_session
from models import User
from schemas.user import UserRead, UserCreate, UserUpdate 

router = APIRouter(prefix="/users", tags=["users"])

#À activer plus tard pour récupérer le user courant (nécessite authentification JWT)
# @router.get("/me", response_model=UserRead)
# def get_my_profile(current_user: User = Depends(get_current_user)):
#     return current_user

#Lister tous les utilisateurs
@router.get("/", response_model=list[UserRead])
def lister_les_utilisateurs(session: Session = Depends(get_session)):
    utilisateurs = session.exec(select(User)).all()
    return utilisateurs

#Lire un utilisateur par son id
@router.get("/{user_id}", response_model=UserRead)
def lire_un_utilisateur(user_id: int, session: Session = Depends(get_session)):
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur

#Créer un nouvel utilisateur
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def creer_un_utilisateur(user: UserCreate, session: Session = Depends(get_session)):
    nouvel_utilisateur = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        password_hashed=user.password,  #À sécuriser plus tard 
        address_user=user.address_user,
        phone=user.phone,
    )
    session.add(nouvel_utilisateur)
    session.commit()
    session.refresh(nouvel_utilisateur)
    return nouvel_utilisateur

#Modifier partiellement un utilisateur (PATCH)
@router.patch("/{user_id}", response_model=UserRead)
def patch_utilisateur(user_id: int, user: UserUpdate, session: Session = Depends(get_session)):
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    #On modifie uniquement les champs reçus (qui ne sont pas None)
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(utilisateur, key, value)
    session.commit()
    session.refresh(utilisateur)
    return utilisateur

#Supprimer un utilisateur
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_un_utilisateur(user_id: int, session: Session = Depends(get_session)):
    utilisateur = session.get(User, user_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    session.delete(utilisateur)
    session.commit()