from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.enumerations import Role
from app.models import Product, User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.security import (
    get_current_user,
    check_admin_employee,
    check_admin,
    check_email_exists,
    check_product_exists,
    check_name_product_exists,
    hash_password
    )
router = APIRouter(prefix="/product", tags=["product"])

# get all products
@router.get("/", response_model=list[ProductRead])
def lister_les_produits(session = Depends(get_session), current_user = Depends(get_current_user)):
    check_admin_employee(current_user)
    produits = session.exec(select(Product)).all()
    return produits

#get one product by id
@router.get("/{product_id}", response_model=ProductRead)
def lire_un_produit_id(product_id: int, session: Session = Depends(get_session),current_user = Depends(get_current_user)):
    produit = session.get(Product, product_id)
    check_product_exists(produit)
    check_admin_employee(current_user)
    return produit

#add new product
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def creer_un_produit(product: ProductCreate, session = Depends(get_session), current_user = Depends(get_current_user)):
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
        stock=product.stock
    )
    session.add(nouveau_produit)
    session.commit()
    session.refresh(nouveau_produit)
    return nouveau_produit

# Patch product
@router.patch("/{product_id}", response_model=ProductRead)
def patch_product(product_id: int, product: ProductUpdate, session = Depends(get_session), current_user = Depends(get_current_user)):
    check_admin_employee(current_user) # vérifier que le produit existe
    produit = session.get(Product, product_id)
    check_product_exists(produit)# vérifier si un autre produit existe avec le meme nom
    existing_product = session.exec(
        select(Product).where(Product.name == product.name)
    ).first()
    check_name_product_exists(existing_product)
    # https://fastapi.tiangolo.com/fr/tutorial/body-updates/#partial-updates-with-patch
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(produit, key, value)
    session.commit()
    session.refresh(produit)
    return produit  

#Supprimer un produit
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_un_produit(product_id: int, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    check_admin_employee(current_user)
    produit = session.get(Product, product_id)
    check_product_exists(produit)
    session.delete(produit)
    session.commit()