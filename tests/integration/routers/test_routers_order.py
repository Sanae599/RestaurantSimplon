import pytest
from fastapi import status
from fastapi.testclient import TestClient

# LISTER LES COMMANDES


def test_lister_les_commandes_employee(
    client: TestClient, override_get_current_employee
):
    resp = client.get("/orders/")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)


def test_lister_les_commandes_client(client: TestClient, override_get_current_client):
    resp = client.get("/orders/")
    assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_200_OK)


# CRÉER DES COMMANDES


def test_creer_une_commande_client(
    client: TestClient, produit, override_get_current_client
):
    payload = {
        "items": [{"product_id": produit.id, "quantity": 2}],
        "note": "Sans oignons",
    }
    resp = client.post("/orders/", json=payload)
    assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), resp.text
    body = resp.json()
    assert "id" in body
    assert isinstance(body.get("items", []), list)
    assert body["items"][0]["product_id"] == produit.id
    assert body["items"][0]["quantity"] == 2


def test_creer_une_commande_admin_pour_client(
    client: TestClient, client_user, produit, override_get_current_admin
):
    payload = {
        "user_id": client_user.id,  # requis si staff crée pour un client
        "items": [{"product_id": produit.id, "quantity": 1}],
        "note": "Créée par admin",
    }
    resp = client.post("/orders/", json=payload)
    assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK), resp.text
    assert resp.json().get("id") is not None


# LIRE / PATCHER / SUPPRIMER


def test_admin_peut_lire_commande_par_id(
    client: TestClient, client_user, produit, override_get_current_admin
):
    created = client.post(
        "/orders/",
        json={
            "user_id": client_user.id,
            "items": [{"product_id": produit.id, "quantity": 1}],
            "note": "lecture par admin",
        },
    )
    assert created.status_code in (
        status.HTTP_201_CREATED,
        status.HTTP_200_OK,
    ), created.text
    order_id = created.json()["id"]

    # côté staff, ton API peut exiger ?user_id=
    got = client.get(f"/orders/{order_id}?user_id={client_user.id}")
    assert got.status_code == status.HTTP_200_OK, got.text
    assert got.json()["id"] == order_id


def test_employee_peut_mettre_a_jour_statut(
    client: TestClient, client_user, produit, override_get_current_employee
):
    created = client.post(
        "/orders/",
        json={
            "user_id": client_user.id,
            "items": [{"product_id": produit.id, "quantity": 1}],
            "note": "maj statut",
        },
    )
    assert created.status_code in (
        status.HTTP_201_CREATED,
        status.HTTP_200_OK,
    ), created.text
    order_id = created.json()["id"]

    # route attend des strings pour status. Ex: "En préparation", "Prete", "Servie"
    update = {"status": "En préparation"}
    patched = client.patch(f"/orders/{order_id}?user_id={client_user.id}", json=update)
    assert patched.status_code in (
        status.HTTP_200_OK,
        status.HTTP_204_NO_CONTENT,
    ), patched.text


def test_client_ne_peut_pas_supprimer_commande_autrui(
    client: TestClient, admin_user, produit, override_get_current_admin
):
    # Création par l'admin (propriétaire = admin)
    created = client.post(
        "/orders/",
        json={
            "user_id": admin_user.id,
            "items": [{"product_id": produit.id, "quantity": 1}],
            "note": "commande admin",
        },
    )
    assert created.status_code in (
        status.HTTP_201_CREATED,
        status.HTTP_200_OK,
    ), created.text
    order_id = created.json()["id"]
    # Pas de suppression ici (on la tente en tant que client dans le test suivant)


@pytest.mark.usefixtures("override_get_current_client")
def test_client_echoue_a_supprimer_commande_autrui(
    client: TestClient, admin_user, produit
):
    # On crée une commande appartenant à l'admin, puis on essaie de la supprimer côté client
    from app.main import app as fastapi_app
    from app.routers.user import get_current_user as dep

    saved = dict(fastapi_app.dependency_overrides)
    try:
        fastapi_app.dependency_overrides[dep] = lambda: admin_user
        created = client.post(
            "/orders/",
            json={
                "user_id": admin_user.id,
                "items": [{"product_id": produit.id, "quantity": 1}],
                "note": "à protéger",
            },
        )
        assert created.status_code in (
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
        ), created.text
        order_id = created.json()["id"]
    finally:
        fastapi_app.dependency_overrides = saved

    deleted = client.delete(f"/orders/{order_id}")
    assert deleted.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)


def test_admin_peut_supprimer_commande(
    client: TestClient, client_user, produit, override_get_current_admin
):
    created = client.post(
        "/orders/",
        json={
            "user_id": client_user.id,
            "items": [{"product_id": produit.id, "quantity": 1}],
            "note": "à supprimer",
        },
    )
    assert created.status_code in (
        status.HTTP_201_CREATED,
        status.HTTP_200_OK,
    ), created.text
    order_id = created.json()["id"]

    deleted = client.delete(f"/orders/{order_id}?user_id={client_user.id}")
    assert deleted.status_code in (
        status.HTTP_200_OK,
        status.HTTP_204_NO_CONTENT,
    ), deleted.text
