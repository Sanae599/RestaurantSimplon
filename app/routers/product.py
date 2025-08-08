from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from db import get_session
from models import Product, User
from schemas.product import ProductRead, ProductCreate, ProductUpdate 
from security import get_current_user
from enumerations import Role

router = APIRouter(prefix="/product", tags=["product"])

# get all products
@router.get("/", response_model=list[ProductRead])
def lister_les_produits(session = Depends(get_session), current_user = Depends(get_current_user)):
    produits = session.exec(select(Product)).all()
    if current_user.role not in (Role.EMPLOYEE, Role.ADMIN):
        raise HTTPException(status_code=403, detail="Réservée au personnel")
    return produits

#get one product by id
@router.get("/{product_id}", response_model=ProductRead)
def lire_un_produit_id(product_id: int, session: Session = Depends(get_session),current_user = Depends(get_current_user)):
    produit = session.get(Product, product_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    if current_user.role not in (Role.EMPLOYEE, Role.ADMIN):
        raise HTTPException(status_code=403, detail="Réservée au personnel")
    return produit

#add new product
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def creer_un_produit(product: ProductCreate, session = Depends(get_session), current_user = Depends(get_current_user)):
    nouveau_produit = Product(
        name=product.name,
        unit_price=product.unit_price,
        category=product.category,
        description=product.description,
        stock=product.stock
    )
    if current_user.role not in (Role.EMPLOYEE, Role.ADMIN):
        raise HTTPException(status_code=403, detail="Réservée au personnel.")
    session.add(nouveau_produit)
    session.commit()
    session.refresh(nouveau_produit)
    return nouveau_produit

# Patch product
@router.patch("/{product_id}", response_model=ProductRead)
def patch_product(product_id: int, product: ProductUpdate, session = Depends(get_session), current_user = Depends(get_current_user)):
    if current_user.role not in (Role.EMPLOYEE, Role.ADMIN):
        raise HTTPException(status_code=403, detail="Réservée au personnel.")
    produit = session.get(Product, product_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
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
    if current_user.role not in (Role.ADMIN,Role.EMPLOYEE):
        raise HTTPException(status_code=403, detail="Réservée au personnel.")
    produit = session.get(Product, product_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    session.delete(produit)
    session.commit()