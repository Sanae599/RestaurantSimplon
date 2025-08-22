from datetime import date as dt_date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.db import get_session
from app.enumerations import Role, Status
from app.models import Order, OrderItem, Product, User
from app.schemas.order import (
    OrderCreateWithItems,
    OrderItemInOrderRead,
    OrderPatchWithItems,
    OrderReadWithItems,
)
from app.security import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=list[OrderReadWithItems])
def lister_les_commandes(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère la liste de toutes les commandes.

    - Accessible uniquement aux **admins** et **employés**.
    - Retourne les commandes avec leurs articles associés.
    """
    if current_user.role not in [Role.ADMIN, Role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les employées peuvent lister les commandes.",
        )
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
                product_name=(oi.product.name if oi.product else ""),
                quantity=oi.quantity,
            )
            for oi in c.order_items
        ]
        result.append(dto)
    return result

@router.get("/by-date", response_model=list[OrderReadWithItems])
def lire_commandes_par_date(
    date: dt_date,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère les commandes créées à une date donnée.

    - Accessible uniquement aux **admins** et **employés**.
    - Retourne les commandes avec leurs articles.
    """
    if current_user.role not in [Role.ADMIN, Role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les employées peuvent voir les commandes par date.",
        )

    stmt = (
        select(Order)
        .where(func.date(Order.created_at) == date)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    )

    rows = session.exec(stmt).all()
    result: list[OrderReadWithItems] = []
    for c in rows:
        dto = OrderReadWithItems.model_validate(c, from_attributes=True)
        dto.items = [
            OrderItemInOrderRead(
                product_id=oi.product_id,
                product_name=(oi.product.name if oi.product else ""),
                quantity=oi.quantity,
            )
            for oi in c.order_items
        ]
        result.append(dto)
    return result


# Lire par utilisateur — client = lui-même ; staff = n'importe qui
@router.get("/user/{user_id}", response_model=list[OrderReadWithItems])
def lire_les_commandes_par_utilisateur(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère les commandes d’un utilisateur donné.

    - Un **client** ne peut voir que ses propres commandes.
    - Les **admins** et **employés** peuvent consulter celles de n’importe quel utilisateur.
    """
    if current_user.role == Role.CLIENT and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit"
        )

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
                quantity=oi.quantity,
            )
            for oi in c.order_items
        ]
        result.append(dto)
    return result

@router.get("/{order_id}", response_model=OrderReadWithItems)
def lire_une_commande_par_orderid(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère une commande spécifique par son ID.

    - Un client ne peut accéder qu’à ses propres commandes.
    - Les admins et employés peuvent accéder à toutes les commandes.
    """
    c = session.exec(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    if current_user.role == Role.CLIENT and c.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit"
        )

    dto = OrderReadWithItems.model_validate(c, from_attributes=True)
    dto.items = [
        OrderItemInOrderRead(
            product_id=oi.product_id,
            product_name=(oi.product.name if oi.product else ""),
            quantity=oi.quantity,
        )
        for oi in c.order_items
    ]
    return dto


# Créer — client = pour lui ; staff = pour un user existant
@router.post(
    "/", response_model=OrderReadWithItems, status_code=status.HTTP_201_CREATED
)
def creer_une_commande(
    payload: OrderCreateWithItems,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Crée une nouvelle commande.

    - Un **client** crée une commande uniquement pour lui-même.
    - Les **admins** et **employés** peuvent créer une commande pour n’importe quel utilisateur existant.
    - La commande doit contenir au moins un article.
    """
    if not payload.items:
        raise HTTPException(
            status_code=422, detail="La commande doit contenir au moins un article."
        )

    if current_user.role == Role.CLIENT:
        user_id = current_user.id
    else:
        if payload.user_id is None:
            raise HTTPException(400, "user_id requis pour le staff.")
        target = session.get(User, payload.user_id)
        if not target:
            raise HTTPException(404, "Utilisateur cible introuvable")
        user_id = payload.user_id

    order = Order(user_id=user_id, total_amount=0.0, status=Status.EN_PREPARATION)
    session.add(order)
    session.flush()

    total = 0.0
    consolidated: dict[int, int] = {}
    for it in payload.items:
        consolidated[it.product_id] = consolidated.get(it.product_id, 0) + it.quantity

    for product_id, qty in consolidated.items():
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(404, f"Produit {product_id} introuvable")
        if qty <= 0:
            raise HTTPException(status_code=422, detail="La quantité doit être ≥ 1.")
        session.add(OrderItem(order_id=order.id, product_id=product_id, quantity=qty))
        total += float(product.unit_price) * qty

    order.total_amount = round(total, 2)
    session.commit()

    c = session.exec(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    ).first()
    dto = OrderReadWithItems.model_validate(c, from_attributes=True)
    dto.items = [
        OrderItemInOrderRead(
            product_id=oi.product_id,
            product_name=(oi.product.name if oi.product else ""),
            quantity=oi.quantity,
        )
        for oi in c.order_items
    ]
    return dto

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_une_commande(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Supprime une commande par son ID.

    - Accessible uniquement aux admins et employés.
    - Retourne un code 204 si la suppression est réussie.
    """
    if current_user.role not in [Role.ADMIN, Role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les employées peuvent supprimer des commandes.",
        )
    commande = session.get(Order, order_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    session.delete(commande)
    session.commit()

@router.patch("/{order_id}", response_model=OrderReadWithItems)
def patch_commande(
    order_id: int,
    payload: OrderPatchWithItems,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Met à jour une commande existante (patch).

    - Accessible uniquement aux admins et employés.
    - Permet de modifier : utilisateur associé, statut, et articles de la commande.
    - Recalcule automatiquement le montant total.
    """
    if current_user.role not in [Role.ADMIN, Role.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les employées peuvent modifier les commandes.",
        )

    order = session.exec(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.order_items))
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    if payload.user_id is not None:
        target = session.get(User, payload.user_id)
        if not target:
            raise HTTPException(status_code=404, detail="Utilisateur cible introuvable")
        order.user_id = payload.user_id
    if payload.status is not None:
        order.status = payload.status

    session.add(order)
    session.flush()

    if payload.items is not None:
        for oi in list(order.order_items):
            session.delete(oi)
        session.flush()
        consolidated: dict[int, int] = {}
        for it in payload.items:
            consolidated[it.product_id] = (
                consolidated.get(it.product_id, 0) + it.quantity
            )
        for product_id, quantity in consolidated.items():
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Produit {product_id} introuvable"
                )
            if quantity <= 0:
                raise HTTPException(
                    status_code=422, detail="La quantité doit être ≥ 1."
                )
            session.add(
                OrderItem(order_id=order.id, product_id=product_id, quantity=quantity)
            )

    session.flush()
    fresh = session.exec(
        select(OrderItem)
        .where(OrderItem.order_id == order.id)
        .options(selectinload(OrderItem.product))
    ).all()
    total = 0.0
    for oi in fresh:
        product = oi.product or session.get(Product, oi.product_id)
        if product:
            total += float(product.unit_price) * oi.quantity
    order.total_amount = round(total, 2)
    session.add(order)
    session.commit()

    c = session.exec(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.order_items).selectinload(OrderItem.product))
    ).first()
    dto = OrderReadWithItems.model_validate(c, from_attributes=True)
    dto.items = [
        OrderItemInOrderRead(
            product_id=oi.product_id,
            product_name=(oi.product.name if oi.product else ""),
            quantity=oi.quantity,
        )
        for oi in c.order_items
    ]
    return dto
