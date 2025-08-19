import pytest
from pydantic import ValidationError
from app.schemas.order import (
    OrderItemCreateInOrder,
    OrderCreateWithItems,
)

# OrderItemCreateInOrder
def test_order_item_quantity_valid():
    """
    Cas valide : quantity >= 1 doit être accepté
    """
    item = OrderItemCreateInOrder(product_id=1, quantity=3)
    assert item.product_id == 1
    assert item.quantity == 3

@pytest.mark.parametrize("bad_qty", [0, -1, -5])
def test_order_item_quantity_invalid(bad_qty):
    """
    Cas invalide : quantity <= 0 doit lever une erreur de validation.
    On s'attend à une ValidationError (Pydantic encapsule nos ValueError).
    """
    with pytest.raises(ValidationError) as exc:
        OrderItemCreateInOrder(product_id=1, quantity=bad_qty)

    # Message défini dans notre validator:
    #   "La quantité doit être ≥ 1."
    assert "La quantité doit être ≥ 1." in str(exc.value)
#Cas invalides (0, -1, -5) → rejetés correctement

# OrderCreateWithItems
def test_order_create_with_items_valid_minimal():
    """
    Cas valide : une commande avec au moins 1 item.
    user_id peut être None (côté route on utilisera le user connecté)
    """
    order = OrderCreateWithItems(
        user_id=None,
        items=[OrderItemCreateInOrder(product_id=10, quantity=2)]
    )
    assert len(order.items) == 1
    assert order.items[0].product_id == 10
    assert order.items[0].quantity == 2


def test_order_create_with_items_empty_list():
    """
    Cas invalide : items = [] (vide) -> le validator doit refuser
    """
    with pytest.raises(ValidationError) as exc:
        OrderCreateWithItems(user_id=None, items=[])
    assert "La commande doit contenir au moins un article." in str(exc.value)