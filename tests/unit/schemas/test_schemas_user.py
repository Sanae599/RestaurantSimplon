import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate


def test_user_create():
    """
    Vérifie la création d'un utilisateur via le schéma UserCreate.

    Étapes du test :
        1. Créer un utilisateur avec des valeurs valides.
        2. Vérifier que le prénom est correctement nettoyé (strip des espaces).

    Assertions :
        - first_name est égal à "AA" après nettoyage.
    """
    user = UserCreate(
        first_name="AA  ",
        last_name="BB",
        email="vincent@test.fr",
        password="password",
        address_user="123 rue aaa",
        phone="0613179351",
    )
    assert user.first_name == "AA"


def test_user_create_valid_phone():
    """
    Vérifie que UserCreate accepte un numéro de téléphone valide.

    Étapes du test :
        1. Créer un utilisateur avec un numéro de téléphone correct.
        2. Vérifier que le champ phone contient la valeur attendue.

    Assertions :
        - phone est égal au numéro fourni.
    """
    user = UserCreate(
        first_name="AA",
        last_name="BB",
        email="vincent@test.fr",
        password="securepassword123",
        address_user="123 Rue aaa",
        phone="0612345678",
    )
    assert user.phone == "0612345678"


@pytest.mark.parametrize(
    "bad_phone",
    [
        "123456789",
        "012345678",
        "01234567890",
    ],
)
def test_user_create_invalid_phone(bad_phone):
    """
    Vérifie que UserCreate lève une ValidationError pour un numéro de téléphone invalide.

    Étapes du test :
        1. Tenter de créer un utilisateur avec un numéro invalide.
        2. S'assurer qu'une ValidationError est levée.

    Paramètres :
        bad_phone (str) : numéro de téléphone invalide testé.

    Assertions :
        - La création lève une ValidationError.
    """
    with pytest.raises(ValidationError) as excinfo:
        UserCreate(
            first_name="AA",
            last_name="BB",
            email="vincent@test.fr",
            password="password123",
            address_user="123 rue aaa",
            phone=bad_phone,
        )
    assert excinfo.type is ValidationError


def test_user_create_valid_email():
    """
    Vérifie que UserCreate accepte un email valide.

    Étapes du test :
        1. Créer un utilisateur avec un email correct.
        2. Vérifier que le champ email contient la valeur attendue.

    Assertions :
        - email est égal à l'email fourni.
    """
    user = UserCreate(
        first_name="AA",
        last_name="BB",
        email="vincent@test.fr",
        password="password123",
        address_user="123 rue aaa",
        phone="0612345678",
    )
    assert user.email == "vincent@test.fr"


@pytest.mark.parametrize(
    "bad_email",
    ["vincent", "vincent@", "vincent@test", "vincent@.fr", "vincent@@test.fr"],
)
def test_user_create_invalid_email(bad_email):
    """
    Vérifie que UserCreate lève une ValidationError pour un email invalide.

    Étapes du test :
        1. Tenter de créer un utilisateur avec un email incorrect.
        2. S'assurer qu'une ValidationError est levée.

    Paramètres :
        bad_email (str) : email invalide testé.

    Assertions :
        - La création lève une ValidationError.
    """
    with pytest.raises(ValidationError) as excinfo:
        UserCreate(
            first_name="AA",
            last_name="BB",
            email=bad_email,
            password="password123",
            address_user="123 rue aaa",
            phone="0612345678",
        )
    assert excinfo.type is ValidationError


# UPDATE
def test_user_update_valid_phone():
    """
    Vérifie que UserUpdate accepte un numéro de téléphone valide.

    Étapes du test :
        1. Créer une instance UserUpdate avec un numéro correct.
        2. Vérifier que le champ phone contient la valeur attendue.

    Assertions :
        - phone est égal au numéro fourni.
    """
    user = UserUpdate(phone="0612345678")
    assert user.phone == "0612345678"


@pytest.mark.parametrize(
    "bad_phone",
    [
        "987654321",
        "06123",
        "061234567890",
    ],
)
def test_user_update_invalid_phone(bad_phone):
    """
    Vérifie que UserUpdate lève une ValidationError pour un numéro de téléphone invalide.

    Étapes du test :
        1. Tenter de mettre à jour le téléphone avec une valeur incorrecte.
        2. S'assurer qu'une ValidationError est levée.

    Paramètres :
        bad_phone (str) : numéro de téléphone invalide testé.

    Assertions :
        - La mise à jour lève une ValidationError.
    """
    with pytest.raises(ValidationError) as excinfo:
        UserUpdate(phone=bad_phone)

    assert excinfo.type is ValidationError
