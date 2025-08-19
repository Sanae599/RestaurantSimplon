import pytest
from pydantic import ValidationError
from datetime import datetime, timezone

from app.models import Order

def test_order_ok_minimal_types():
    """
    Cas valide minimal :
    user_id=int, total_amount=float, status=str
    """
    o = Order(user_id=1, total_amount=12.5, status="En préparation")
    assert isinstance(o.user_id, int)
    assert isinstance(o.total_amount, float)
    assert isinstance(o.status, str)

def test_order_created_at_default_is_datetime_tzaware():
    """
    Cas valide : created_at a une valeur par défaut de type datetime timezone-aware (UTC)
    """
    o = Order(user_id=1, total_amount=9.99, status="En préparation")
    assert isinstance(o.created_at, datetime)
    assert o.created_at.tzinfo is not None
    assert o.created_at.tzinfo == timezone.utc

