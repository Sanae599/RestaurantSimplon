from datetime import datetime
import pytest
from pydantic import ValidationError
from app.models import Product  

def test_product_valid_enum():
    """Vérifie qu'un Product accepte une catégorie valide (Enum)."""
    product = Product(
        name="Pizza Margherita",
        unit_price=12.5,
        category="Plat principal",
        description="Pizza classique",
        stock=20,
    )
    assert isinstance(product.created_at, datetime)