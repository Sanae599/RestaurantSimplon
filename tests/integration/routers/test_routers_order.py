import pytest
from fastapi.testclient import TestClient
from fastapi import status

#LISTER LES COMMANDES

def test_lister_les_commandes_employee(client: TestClient, override_get_current_employee):
    response = client.get("/orders/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_lister_les_commandes_client(client: TestClient, override_get_current_client):
    response = client.get("/orders/")
    assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_200_OK)
#Cas invalide

#CRÉER UNE COMMANDE

def test_creer_une_commande_client(client: TestClient, produit, override_get_current_client):
    data = {
        "items": [{"product_id": produit.id, "quantity": 2}]    }
    response = client.post("/orders/", json=data)
    assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), response.text
    body = response.json()
    assert "id" in body
    assert isinstance(body.get("items", []), list)
    assert body["items"][0]["product_id"] == produit.id
    assert body["items"][0]["quantity"] == 2

def test_creer_une_commande_admin_pour_un_client(client: TestClient, client_user, produit, override_get_current_admin):
    # staff crée pour un client -> body doit contenir user_id
    data = {
        "user_id": client_user.id,
        "items": [{"product_id": produit.id, "quantity": 1}]
    }
    response = client.post("/orders/", json=data)
    assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), response.text
    assert response.json().get("id") is not None


#LIRE / PATCHER / SUPPRIMER UNE COMMANDE

def test_admin_peut_lire_une_commande_par_id(client: TestClient, client_user, produit, override_get_current_admin):
    created = client.post("/orders/", json={
        "user_id": client_user.id,  # requis pour STAFF
        "items": [{"product_id": produit.id, "quantity": 1}]    })
    assert created.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), created.text
    order_id = created.json()["id"]

    # lecture par staff -> user_id en query
    resp = client.get(f"/orders/{order_id}?user_id={client_user.id}")
    assert resp.status_code == status.HTTP_200_OK, resp.text
    assert resp.json()["id"] == order_id


def test_employee_peut_mettre_a_jour_statut(client: TestClient, client_user, produit, override_get_current_employee):
    created = client.post("/orders/", json={
        "user_id": client_user.id,
        "items": [{"product_id": produit.id, "quantity": 1}]    })
    assert created.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), created.text
    order_id = created.json()["id"]

    update = {"status": "En préparation"} 
    resp = client.patch(f"/orders/{order_id}?user_id={client_user.id}", json=update)
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT), resp.text


def test_client_ne_peut_pas_supprimer_la_commande_d_un_autre(client: TestClient, admin_user, produit, override_get_current_admin):
    # admin crée une commande pour lui-même
    created = client.post("/orders/", json={
        "user_id": admin_user.id,
        "items": [{"product_id": produit.id, "quantity": 1}]    })
    assert created.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), created.text
    order_id = created.json()["id"]
    # On ne supprime pas ici (on le fera côté client dans le test suivant)
#Cas invalide


@pytest.mark.usefixtures("override_get_current_client")
def test_client_echoue_a_supprimer_commande_autrui(client: TestClient, admin_user, produit):
    # Créer une commande appartenant à l'admin, puis tenter de la supprimer en tant que client
    from app.main import app as fastapi_app
    from app.routers.user import get_current_user as dep

    saved = dict(fastapi_app.dependency_overrides)
    try:
        fastapi_app.dependency_overrides[dep] = lambda: admin_user
        created = client.post("/orders/", json={
            "user_id": admin_user.id,
            "items": [{"product_id": produit.id, "quantity": 1}]        })
        assert created.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), created.text
        order_id = created.json()["id"]
    finally:
        fastapi_app.dependency_overrides = saved

    deleted = client.delete(f"/orders/{order_id}")
    assert deleted.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
#Cas invalide


def test_admin_peut_supprimer_une_commande(client: TestClient, client_user, produit, override_get_current_admin):
    created = client.post("/orders/", json={
        "user_id": client_user.id,
        "items": [{"product_id": produit.id, "quantity": 1}]    })
    assert created.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), created.text
    order_id = created.json()["id"]

    deleted = client.delete(f"/orders/{order_id}?user_id={client_user.id}")
    assert deleted.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT), deleted.text
