from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Delivery
from app.schemas.delivery import DeliveryCreate, DeliveryRead, DeliveryUpdate

router = APIRouter(prefix="/delivery", tags=["delivery"])

@router.get("/", response_model=list[DeliveryRead])
def lister_les_livraisons(session: Session = Depends(get_session)):
    """
    Récupère la liste de toutes les livraisons.

    Args:
        session (Session, optional): Session de base de données injectée par FastAPI.

    Returns:
        list[DeliveryRead]: Liste des livraisons enregistrées en base.
    """
    produits = session.exec(select(Delivery)).all()
    return produits

@router.get("/{delivery_id}", response_model=DeliveryRead)
def lire_une_livraison_id(delivery_id: int, session: Session = Depends(get_session)):
    """
    Récupère une livraison spécifique par son identifiant.

    Args:
        delivery_id (int): Identifiant unique de la livraison à récupérer.
        session (Session, optional): Session de base de données injectée par FastAPI.

    Raises:
        HTTPException: Erreur 404 si la livraison n'existe pas.

    Returns:
        DeliveryRead: Livraison correspondant à l'identifiant fourni.
    """
    delivery = session.get(Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Livraison non trouvée")
    return delivery
