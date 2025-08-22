from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.enumerations import Category
from app.models import Product

# TEST LISTER LES PRODUITS
def test_lister_les_produits_admin(client, produit, override_get_current_admin):
    """
    Vérifie qu'un administrateur peut lister tous les produits.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        produit (Product): Instance de produit préexistante pour test.
        override_get_current_admin: Fixture qui simule un utilisateur admin.

    Assertions:
        - Le status code de la réponse est 200.
        - La réponse est une liste de produits.
        - La liste contient au moins un produit.
        - Le premier produit a le même nom que le produit de test.
    """
    response = client.get("/product/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == produit.name


def test_lister_les_produits_client(client, produit, override_get_current_client):
    """
    Vérifie qu'un client n'a pas le droit de lister les produits.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        produit (Product): Instance de produit préexistante pour test.
        override_get_current_client: Fixture qui simule un utilisateur client.

    Assertions:
        - Le status code de la réponse est 403 (interdit pour le client).
    """
    response = client.get("/product/")
    assert response.status_code == 403


# TEST CREER UN PRODUIT
def test_creer_un_produit_admin(client: TestClient, override_get_current_admin):
    """
    Vérifie qu'un administrateur peut créer un nouveau produit.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        override_get_current_admin: Fixture qui simule un utilisateur admin.

    Assertions:
        - Le status code de la réponse est 201 (créé).
        - Le nom du produit retourné correspond au nom envoyé dans la requête.
    """
    data = {
        "name": "Produit Test",
        "unit_price": 9.99,
        "category": "Plat principal",
        "description": "Description Test",
        "stock": 100,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/product/", json=data)
    assert response.status_code == 201, response.json()
    result = response.json()
    assert result["name"] == data["name"]


def test_creer_un_produit_client(client: TestClient, override_get_current_client):
    """
    Vérifie qu'un client ne peut pas créer de produit.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        override_get_current_client: Fixture qui simule un utilisateur client.

    Assertions:
        - Le status code de la réponse est 403 (interdit pour le client).
    """
    data = {
        "name": "Produit Test",
        "unit_price": 9.99,
        "category": "Plat principal",
        "description": "Description Test",
        "stock": 100,
    }
    response = client.post("/product/", json=data)
    # interdit pour le client
    assert response.status_code == 403


# TEST PATCH UN PRODUIT
def test_patch_product_admin(
    client: TestClient, session: Session, override_get_current_admin
):
    """
    Vérifie qu'un administrateur peut mettre à jour un produit existant.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        session (Session): Session SQLAlchemy/SQLModel pour la DB.
        override_get_current_admin: Fixture qui simule un utilisateur admin.

    Assertions:
        - Le status code de la réponse est 200.
        - Les champs mis à jour (unit_price, stock) sont corrects dans la réponse.
    """
    produit = Product(
        name="Produit Patch",
        unit_price=5.0,
        category="Plat principal",
        description="Desc",
        stock=20,
    )
    session.add(produit)
    session.commit()
    session.refresh(produit)

    update_data = {"unit_price": 7.5, "stock": 30}
    response = client.patch(f"/product/{produit.id}", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["unit_price"] == 7.5
    assert result["stock"] == 30


def test_patch_product_client(
    client: TestClient, session: Session, override_get_current_client
):
    """
    Vérifie qu'un client ne peut pas mettre à jour un produit.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        session (Session): Session SQLAlchemy/SQLModel pour la DB.
        override_get_current_client: Fixture qui simule un utilisateur client.

    Assertions:
        - Le status code de la réponse est 403 (interdit pour le client).
    """
    produit = Product(
        name="Produit Patch",
        unit_price=5.0,
        category="Plat principal",
        description="Desc",
        stock=20,
    )
    session.add(produit)
    session.commit()
    session.refresh(produit)

    update_data = {"unit_price": 7.5, "stock": 30}
    response = client.patch(f"/product/{produit.id}", json=update_data)
    assert response.status_code == 403  # interdit pour le client


# TEST SUPPRIMER UN PRODUIT
def test_supprimer_un_produit_admin(
    client: TestClient, session: Session, override_get_current_admin
):
    """
    Vérifie qu'un administrateur peut supprimer un produit existant.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        session (Session): Session SQLAlchemy/SQLModel pour la DB.
        override_get_current_admin: Fixture qui simule un utilisateur admin.

    Assertions:
        - Le status code de la réponse est 204 (supprimé).
        - Le produit n'existe plus en base.
    """
    produit = Product(
        name="Produit Delete",
        unit_price=1.0,
        category="Plat principal",
        description="Desc",
        stock=10,
    )
    session.add(produit)
    session.commit()
    session.refresh(produit)

    response = client.delete(f"/product/{produit.id}")
    assert response.status_code == 204
    assert session.get(Product, produit.id) is None


def test_supprimer_un_produit_client(
    client: TestClient, session: Session, override_get_current_client
):
    """
    Vérifie qu'un client ne peut pas supprimer un produit.

    Args:
        client (TestClient): Client FastAPI pour faire les requêtes.
        session (Session): Session SQLAlchemy/SQLModel pour la DB.
        override_get_current_client: Fixture qui simule un utilisateur client.

    Assertions:
        - Le status code de la réponse est 403 (interdit pour le client).
    """
    produit = Product(
        name="Produit Delete",
        unit_price=1.0,
        category="Plat principal",
        description="Desc",
        stock=10,
    )
    session.add(produit)
    session.commit()
    session.refresh(produit)

    response = client.delete(f"/product/{produit.id}")
    assert response.status_code == 403  # interdit pour le client
