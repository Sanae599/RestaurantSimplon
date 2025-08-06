from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, and_
from db import get_session
from models import OrderItem
from schemas.order_item import OrderItemRead, OrderItemCreate, OrderItemUpdate

router = APIRouter(prefix="/orderitem", tags=["orderitem"])

# Lister tous les order items
@router.get("/", response_model=list[OrderItemRead])
def list_order_items(session: Session = Depends(get_session)):
    order_items = session.exec(select(OrderItem)).all()
    return order_items

# Lire tous les items d'une commande
@router.get("/by-order/{order_id}", response_model=list[OrderItemRead])
def list_order_items_by_order(order_id: int, session: Session = Depends(get_session)):
    items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()
    return items

# Lire tous les items d'un produit
@router.get("/by-product/{product_id}", response_model=list[OrderItemRead])
def list_order_items_by_product(product_id: int, session: Session = Depends(get_session)):
    items = session.exec(
        select(OrderItem).where(OrderItem.product_id == product_id)
    ).all()
    return items

# Lire un order item précis (clé composite)
@router.get("/{order_id}/{product_id}", response_model=OrderItemRead)
def get_order_item(order_id: int, product_id: int, session: Session = Depends(get_session)):
    order_item = session.exec(
        select(OrderItem).where(
            and_(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id
            )
        )
    ).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item pas trouvé")
    return order_item

# Créer un order item (on reçoit order_id et product_id explicitement)
@router.post("/", response_model=OrderItemRead, status_code=status.HTTP_201_CREATED)
def create_order_item(
    order_id: int,
    product_id: int,
    order_item: OrderItemCreate,
    session: Session = Depends(get_session)
):
    db_order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=order_item.quantity
    )
    session.add(db_order_item)
    session.commit()
    session.refresh(db_order_item)
    return db_order_item

# Modifier un order item (PATCH via clé composite)
@router.patch("/{order_id}/{product_id}", response_model=OrderItemRead)
def patch_order_item(order_id: int, product_id: int, order_item: OrderItemUpdate, session: Session = Depends(get_session)):
    db_order_item = session.exec(
        select(OrderItem).where(
            and_(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id
            )
        )
    ).first()
    if not db_order_item:
        raise HTTPException(status_code=404, detail="Order item pas trouvé")
    update_data = order_item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order_item, key, value)
    session.commit()
    session.refresh(db_order_item)
    return db_order_item

# Supprimer un order item précis
@router.delete("/{order_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_id: int, product_id: int, session: Session = Depends(get_session)):
    db_order_item = session.exec(
        select(OrderItem).where(
            and_(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id
            )
        )
    ).first()
    if not db_order_item:
        raise HTTPException(status_code=404, detail="Order item pas trouvé")
    session.delete(db_order_item)
    session.commit()
