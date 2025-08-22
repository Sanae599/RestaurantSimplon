import pytest
from sqlmodel import select

from app.enumerations import Role
from app.models import User


def test_create_user(client, session, admin_user, override_get_current_admin):
    """
    Teste la création d'un nouvel utilisateur via l'API en tant qu'administrateur.

    Étapes du test :
        1. Préparer les données d'un nouvel utilisateur.
        2. Envoyer une requête POST sur la route "/user/".
        3. Vérifier que la réponse a un status code 201 (créé).
        4. Vérifier que les données retournées correspondent aux données envoyées.
        5. Vérifier que l'utilisateur a bien été ajouté en base de données avec les bons attributs.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        session (Session): Session SQLAlchemy/SQLModel pour accéder à la base de données.
        admin_user (User): Utilisateur administrateur pour les tests.
        override_get_current_admin: Fixture qui simule un utilisateur admin.

    Assertions:
        - Le status code de la réponse est 201.
        - L'email et le rôle de l'utilisateur dans la réponse sont corrects.
        - L'utilisateur existe bien en base.
        - Tous les attributs de l'utilisateur en base correspondent aux données envoyées.
    """
    new_user_data = {
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "password": "password123",
        "role": "CLIENT",
        "address_user": "101 New Street",
        "phone": "0613179351",
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
