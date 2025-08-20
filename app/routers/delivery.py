from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Delivery
from app.schemas.delivery import DeliveryCreate, DeliveryRead, DeliveryUpdate

router = APIRouter(prefix="/delivery", tags=["delivery"])


# get all delivery
@router.get("/", response_model=list[DeliveryRead])
def lister_les_livraisons(session: Session = Depends(get_session)):
    produits = session.exec(select(Delivery)).all()
    return produits


# get one product by id
@router.get("/{delivery_id}", response_model=DeliveryRead)
def lire_une_livraison_id(delivery_id: int, session: Session = Depends(get_session)):
    delivery = session.get(Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Livraison non trouvé")
    return delivery
