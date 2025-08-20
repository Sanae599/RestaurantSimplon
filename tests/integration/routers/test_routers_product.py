import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import Product
from app.enumerations import Category
from datetime import datetime, timezone



# TEST LISTER LES PRODUITS

def test_lister_les_produits_admin(client, produit, override_get_current_admin):
    response = client.get("/product/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0             
    assert data[0]["name"] == produit.name

def test_lister_les_produits_client(client, produit, override_get_current_client):
    response = client.get("/product/")
    # Ici le client peut juste lire, donc 200 ou 403 selon ton endpoint
    # Si tu veux interdire la liste pour le client, 403
    assert response.status_code == 403  


# TEST CREER UN PRODUIT

def test_creer_un_produit_admin(client: TestClient, override_get_current_admin):
    data = {
        "name": "Produit Test",
        "unit_price": 9.99,
        "category": "Plat principal",
        "description": "Description Test",
        "stock": 100,
        "created_at": datetime.now(timezone.utc).isoformat()  

    }
    response = client.post("/product/", json=data)
    assert response.status_code == 201, response.json()  
    result = response.json()
    assert result["name"] == data["name"]

def test_creer_un_produit_client(client: TestClient, override_get_current_client):
    data = {
        "name": "Produit Test",
        "unit_price": 9.99,
        "category": "Plat principal",
        "description": "Description Test",
        "stock": 100
    }
    response = client.post("/product/", json=data)
    # interdit pour le client
    assert response.status_code == 403


# TEST PATCH (mettre à jour) UN PRODUIT

def test_patch_product_admin(client: TestClient, session: Session, override_get_current_admin):
    produit = Product(name="Produit Patch", unit_price=5.0, category="Plat principal", description="Desc", stock=20)
    session.add(produit)
    session.commit()
    session.refresh(produit)

    update_data = {"unit_price": 7.5, "stock": 30}
    response = client.patch(f"/product/{produit.id}", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["unit_price"] == 7.5
    assert result["stock"] == 30

def test_patch_product_client(client: TestClient, session: Session, override_get_current_client):
    produit = Product(name="Produit Patch", unit_price=5.0, category="Plat principal", description="Desc", stock=20)
    session.add(produit)
    session.commit()
    session.refresh(produit)

    update_data = {"unit_price": 7.5, "stock": 30}
    response = client.patch(f"/product/{produit.id}", json=update_data)
    assert response.status_code == 403  # interdit pour le client


# TEST SUPPRIMER UN PRODUIT

def test_supprimer_un_produit_admin(client: TestClient, session: Session, override_get_current_admin):
    produit = Product(name="Produit Delete", unit_price=1.0, category="Plat principal", description="Desc", stock=10)
    session.add(produit)
    session.commit()
    session.refresh(produit)

    response = client.delete(f"/product/{produit.id}")
    assert response.status_code == 204
    assert session.get(Product, produit.id) is None

def test_supprimer_un_produit_client(client: TestClient, session: Session, override_get_current_client):
    produit = Product(name="Produit Delete", unit_price=1.0, category="Plat principal", description="Desc", stock=10)
    session.add(produit)
    session.commit()
    session.refresh(produit)

    response = client.delete(f"/product/{produit.id}")
    assert response.status_code == 403  # interdit pour le client