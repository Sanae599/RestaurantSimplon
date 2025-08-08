from datetime import date as dt_date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import Query
from sqlalchemy import func
from db import get_session
from security import get_current_user
from models import Order, OrderItem, Product, User
from schemas.order import OrderRead, OrderUpdate, OrderReadWithItems, OrderItemInOrderRead, OrderCreateWithItems
from enumerations import Status

router = APIRouter(prefix="/orders", tags=["orders"])

#Lister tous les commandes
@router.get("/", response_model=list[OrderReadWithItems])
def lister_les_commandes(session: Session = Depends(get_session)):
    rows = session.exec(
        select(Order).options(
            selectinload(Order.order_items).selectinload(OrderItem.product) 
        )
    ).all()

    result: list[OrderReadWithItems] = []
    for c in rows:
        dto = OrderReadWithItems.model_validate(c, from_attributes=True)
        dto.items = [
            OrderItemInOrderRead(
                product_id=oi.product_id,
                product_name=(oi.product.name if oi.product else ""),  # fallback si produit manquant
                quantity=oi.quantity
            )
            for oi in c.order_items
        ]
        result.append(dto)
    return result

#Lire les commandes par date
@router.get("/by-date", response_model=list[OrderReadWithItems])
def lire_commandes_par_date(
    date: dt_date,  # FastAPI parse tout seul YYYY-MM-DD
    session: Session = Depends(get_session)
):
    rows = session.exec(
        select(Order)
        .where(func.date(Order.created_at) == date)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    ).all()

    result: list[OrderReadWithItems] = []
    for c in rows:
        dto = OrderReadWithItems.model_validate(c, from_attributes=True)
        dto.items = [
            OrderItemInOrderRead(
                product_id=oi.product_id,
                product_name=(oi.product.name if oi.product else ""),
                quantity=oi.quantity
            )
            for oi in c.order_items
        ]
        result.append(dto)
    return result

#lire les commandes par order id
@router.get("/{order_id}", response_model=OrderReadWithItems)
def lire_une_commande_par_orderid(order_id: int, session: Session = Depends(get_session)):
    c = session.exec(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    dto = OrderReadWithItems.model_validate(c, from_attributes=True)
    dto.items = [
        OrderItemInOrderRead(
            product_id=oi.product_id,
            product_name=(oi.product.name if oi.product else ""),
            quantity=oi.quantity
        )
        for oi in c.order_items
    ]
    return dto

# Lire les commandes par client 
@router.get("/user/{user_id}", response_model=list[OrderReadWithItems])
def lire_les_commandes_par_utilisateur(user_id: int, session: Session = Depends(get_session)):
    rows = session.exec(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    ).all()

    result: list[OrderReadWithItems] = []
    for c in rows:
        dto = OrderReadWithItems.model_validate(c, from_attributes=True)
        dto.items = [
            OrderItemInOrderRead(
                product_id=oi.product_id,
                product_name=(oi.product.name if oi.product else ""),
                quantity=oi.quantity
            )
            for oi in c.order_items
        ]
        result.append(dto)
    return result


#Créer une nouvelle commande
@router.post("/", response_model=OrderReadWithItems, status_code=status.HTTP_201_CREATED)
def creer_une_commande(
    payload: OrderCreateWithItems,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "client":
        user_id = current_user.id                 # on bloque pour un client
    else:
        # staff : user_id obligatoire et doit exister
        if payload.user_id is None:
            raise HTTPException(400, "user_id requis pour le staff.")
        target = session.get(User, payload.user_id)
        if not target:
            raise HTTPException(404, "Utilisateur cible introuvable")
        user_id = payload.user_id

    #on créait  la commande vide
    order = Order(user_id=user_id, total_amount=0.0, status=Status.EN_PREPARATION)
    session.add(order)
    session.flush()  # pour avoir order.id

    #on a créer les items + total
    total = 0.0
    consolidated = {}
    for it in payload.items:
        consolidated[it.product_id] = consolidated.get(it.product_id, 0) + it.quantity

    for product_id, qty in consolidated.items():
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(404, f"Produit {product_id} introuvable")
        if qty <= 0:
            raise HTTPException(422, "La quantité doit être ≥ 1.")
        session.add(OrderItem(order_id=order.id, product_id=product_id, quantity=qty))
        total += float(product.unit_price) * qty

    order.total_amount = round(total, 2)
    session.commit()

    order = session.exec(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    ).first()

    dto = OrderReadWithItems.model_validate(order, from_attributes=True)
    dto.items = [
        OrderItemInOrderRead(
            product_id=oi.product_id,
            product_name=(oi.product.name if oi.product else ""),
            quantity=oi.quantity
        )
        for oi in order.order_items
    ]
    return dto

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