from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db import get_session
from models import Order
from schemas.order import OrderRead, OrderCreate, OrderUpdate 
from enumerations import Status

router = APIRouter(prefix="/orders", tags=["orders"])

#Lister tous les commandes
@router.get("/", response_model=list[OrderRead])
def lister_les_commandes(session: Session = Depends(get_session)):
    commandes = session.exec(select(Order)).all()
    return commandes

# Lire les commandes par client 
@router.get("/user/{user_id}", response_model=list[OrderRead])
def lire_les_commandes_par_utilisateur(user_id: int, session: Session = Depends(get_session)):
    commande = session.exec(select(Order).where(Order.user_id == user_id)).all()
    if not commande:
        raise HTTPException(status_code=404, detail="Aucune commande trouvée pour cet utilisateur")
    return commande


#Lire les commandes par date
@router.get("/by-date", response_model=list[OrderRead])
def lire_commandes_par_date(date: date, session: Session = Depends(get_session)):
    commandes = session.exec(select(Order).where(Order.created_at.cast(date) == date)).all()
    if not commandes:
        raise HTTPException(status_code=404, detail="Aucune commande trouvée à cette date")
    return commandes

#Lire une commande par son id
@router.get("/{order_id}", response_model=OrderRead)
def lire_une_commande(order_id: int, session: Session = Depends(get_session)):
    commande = session.get(Order, order_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return commande


#Créer une nouvelle commande
@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def creer_une_commande(order: OrderCreate, session: Session = Depends(get_session)):
    nouvelle_commande = Order(
        user_id=order.user_id,
        total_amount=0.0,
        status=Status.EN_PREPARATION
    )
    session.add(nouvelle_commande)
    session.commit()
    session.refresh(nouvelle_commande)
    return nouvelle_commande

#Supprimer une commande
@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_une_commande(order_id: int, session: Session = Depends(get_session)):
    commande = session.get(Order, order_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    session.delete(commande)
    session.commit()
    
#Modifier partiellement une commande (PATCH)
@router.patch("/{order_id}", response_model=OrderRead)
def patch_commande(order_id: int, order: OrderUpdate, session: Session = Depends(get_session)):
    commande = session.get(Order, order_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    #On modifie uniquement les champs reçus (qui ne sont pas None)
    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(commande, key, value)
    session.commit()
    session.refresh(commande)
    return commande

#nombre de commande total et calcul du montant total 