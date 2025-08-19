import pytest
from datetime import datetime, timezone
from app.models import User
from pydantic import ValidationError


def test_user_types_valide():
    user = User(
        id=1,
        first_name="AA",
        last_name="BB",
        email="vincent@test.fr",
        role="client",
        password_hashed="test",
        address_user="123 rue aaa",
        phone="0612345678",
        created_at=datetime.now(timezone.utc)
    )

    assert isinstance(user.id, int)
    assert isinstance(user.first_name, str)
    assert isinstance(user.last_name, str)
    assert isinstance(user.email, str) 
    assert "@" in user.email
    assert isinstance(user.role, str)
    assert isinstance(user.password_hashed, str)
    assert isinstance(user.address_user, str)
    assert isinstance(user.phone, str)
    assert isinstance(user.created_at, datetime)

def test_user_optional_fields_none():
    # Check champs optional
    user = User(
        address_user=None,  
        phone=None,        
    )
    assert user.address_user is None
    assert user.phone is None
    assert user.id is None 

