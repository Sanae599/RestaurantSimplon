import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.product import ProductCreate, ProductUpdate
from app.enumerations import Category

# Tests ProductCreate

def test_product_create_valid():
    """
    Cas valide : prix > 0 et stock >= 0
    """
    product = ProductCreate(
        name="Pizza",
        unit_price=12.5,
        category=Category.PLAT_PRINCIPAL,
        description="Délicieuse pizza",
        stock=10,
        created_at=datetime.now()
    )
    assert product.name == "Pizza"
    assert product.unit_price == 12.5
    assert product.stock == 10
    assert product.category == Category.PLAT_PRINCIPAL


@pytest.mark.parametrize("bad_price", [0, -1, -10])
def test_product_create_invalid_unit_price(bad_price):
    """
    Cas invalide : prix <= 0 doit lever une ValidationError
    """
    with pytest.raises(ValidationError) as exc:
        ProductCreate(
            name="Burger",
            unit_price=bad_price,
            category=Category.PLAT_PRINCIPAL,
            description="Burger ",
            stock=5
        )
    assert "Le prix doit être sup à 0€" in str(exc.value)


@pytest.mark.parametrize("bad_stock", [-1, -5, -100])
def test_product_create_invalid_stock(bad_stock):
    """
    Cas invalide : stock < 0 doit lever une ValidationError
    """
    with pytest.raises(ValidationError) as exc:
        ProductCreate(
            name="Salade",
            unit_price=8.0,
            category=Category.ENTREE,
            description="Salade",
            stock=bad_stock
        )
    assert "Le stock ne peut pas être inf à 0." in str(exc.value)



# Tests ProductUpdate

def test_product_update_valid_partial():
    """
    Cas valide : mise à jour partielle avec prix et stock corrects
    """
    product_update = ProductUpdate(
        unit_price=15.0,
        stock=20
    )
    assert product_update.unit_price == 15.0
    assert product_update.stock == 20


@pytest.mark.parametrize("bad_price", [0, -1])
def test_product_update_invalid_unit_price(bad_price):
    """
    Cas invalide : prix <= 0 doit lever une ValidationError
    """
    with pytest.raises(ValidationError) as exc:
        ProductUpdate(unit_price=bad_price)
    assert "Le prix doit être sup à 0€" in str(exc.value)


@pytest.mark.parametrize("bad_stock", [-1, -10])
def test_product_update_invalid_stock(bad_stock):
    """
    Cas invalide : stock < 0 doit lever une ValidationError
    """
    with pytest.raises(ValidationError) as exc:
        ProductUpdate(stock=bad_stock)
    assert "Le stock ne peut pas être inf à 0." in str(exc.value)
