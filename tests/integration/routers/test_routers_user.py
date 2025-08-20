import pytest
from sqlmodel import select
from app.models import User
from app.enumerations import Role

def test_create_user(client, session, admin_user, override_get_current_admin):
    # new user
    new_user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "CLIENT",
        "address_user": "101 New Street",
        "phone": "0613179351"
    }

    # post sur route création user
    response = client.post("/user/", json=new_user_data)

    print("Status code:", response.status_code)
    print("Réponse JSON:", response.json())

    # check response
    assert response.status_code == 201, f"Erreur inattendue: {response.text}"
    response_data = response.json()
    assert response_data["email"] == "newuser@example.com"
    assert response_data["role"] == "client"  

    # check new user in base
    user_in_db = session.exec(
        select(User).where(User.email == "newuser@example.com")
    ).first()

    print("User in DB:", user_in_db)
    print("User role:", user_in_db.role)

    assert user_in_db is not None
    assert user_in_db.first_name == "New"
    assert user_in_db.last_name == "User"
    assert user_in_db.role == Role.CLIENT
    assert user_in_db.address_user == "101 New Street"
    assert user_in_db.phone == "0613179351"