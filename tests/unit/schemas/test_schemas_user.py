import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate


def test_user_create():
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
    with pytest.raises(ValidationError) as excinfo:
        UserUpdate(phone=bad_phone)

    assert excinfo.type is ValidationError
