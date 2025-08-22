from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.enumerations import Role
from app.models import Product, User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.security import (
    check_admin,
    check_admin_employee,
    check_email_exists,
    check_name_product_exists,
    check_product_exists,
    get_current_user,
    hash_password,
)

router = APIRouter(prefix="/product", tags=["product"])

@router.get("/", response_model=list[ProductRead])
def lister_les_produits(
    session=Depends(get_session), current_user=Depends(get_current_user)
):
    """
    Récupère la liste de tous les produits.

    - Accessible uniquement aux admins et employés.
    - Retourne les informations principales des produits.
    """
    check_admin_employee(current_user)
    produits = session.exec(select(Product)).all()
    return produits

@router.get("/{product_id}", response_model=ProductRead)
def lire_un_produit_id(
    product_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Récupère un produit par son ID.

    - Vérifie que le produit existe, sinon lève une exception 404.
    - Accessible uniquement aux admins et employés.
    """
    produit = session.get(Product, product_id)
    check_product_exists(produit)
    check_admin_employee(current_user)
    return produit

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def creer_un_produit(
    product: ProductCreate,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Crée un nouveau produit.

    - Accessible uniquement aux admins et employés.
    - Vérifie qu’aucun autre produit avec le même nom n’existe déjà.
    - Retourne le produit nouvellement créé.
    """
    check_admin_employee(current_user)
    existing_product = session.exec(
        select(Product).where(Product.name == product.name)
    ).first()
    check_name_product_exists(existing_product)
    nouveau_produit = Product(
        name=product.name,
        unit_price=product.unit_price,
        category=product.category,
        description=product.description,
        stock=product.stock,
    )
    session.add(nouveau_produit)
    session.commit()
    session.refresh(nouveau_produit)
    return nouveau_produit


# Patch product
@router.patch("/{product_id}", response_model=ProductRead)
def patch_product(
    product_id: int,
    product: ProductUpdate,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Met à jour partiellement un produit existant.

    - Accessible uniquement aux **admins** et **employés**.
    - Vérifie que le produit existe.
    - Vérifie qu’il n’y a pas de doublon de nom avec un autre produit.
    - Retourne le produit mis à jour.
    """
    # Check que le produit existe
    check_admin_employee(current_user)  
    produit = session.get(Product, product_id)
    check_product_exists(produit)  

    # Check si un autre produit existe avec le meme nom
    existing_product = session.exec(
        select(Product).where(Product.name == product.name)
    ).first()
    check_name_product_exists(existing_product)

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(produit, key, value)

    session.commit()
    session.refresh(produit)
    return produit

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_un_produit(
    product_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Supprime un produit par son ID.

    - Accessible uniquement aux admins et employés.
    - Vérifie que le produit existe avant suppression.
    - Retourne un code 204 si la suppression est réussie.
    """
    check_admin_employee(current_user)
    produit = session.get(Product, product_id)
    check_product_exists(produit)
    session.delete(produit)
    session.commit()
