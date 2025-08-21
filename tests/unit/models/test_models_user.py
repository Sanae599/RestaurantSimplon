from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import User


def test_user_types_valide():
    """
    Vérifie que la création d'un utilisateur avec tous les champs valides produit
    des attributs du type attendu.

    Étapes du test :
        1. Créer un utilisateur avec tous les champs obligatoires renseignés.
        2. Vérifier que chaque attribut a le type attendu.
        3. Vérifier que l'email contient un '@'.

    Assertions :
        - id est un int
        - first_name, last_name, email, role, password_hashed, address_user, phone sont des str
        - email contient '@'
        - created_at est un datetime
    """
    user = User(
        id=1,
        first_name="AA",
        last_name="BB",
        email="vincent@test.fr",
        role="client",
        password_hashed="test",
        address_user="123 rue aaa",
        phone="0612345678",
        created_at=datetime.now(timezone.utc),
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
    """
    Vérifie que les champs optionnels d'un utilisateur peuvent être None.

    Étapes du test :
        1. Créer un utilisateur en laissant address_user et phone à None.
        2. Vérifier que les champs optionnels sont bien None.
        3. Vérifier que l'id par défaut est None.

    Assertions :
        - address_user est None
        - phone est None
        - id est None
    """
    user = User(
        address_user=None,
        phone=None,
    )
    assert user.address_user is None
    assert user.phone is None
    assert user.id is None
