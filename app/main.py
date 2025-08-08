from fastapi import FastAPI
from db import engine, init_db, get_session
from fake_data import *
from routers import user, product, order, delivery, login
from contextlib import asynccontextmanager
import os

app = FastAPI()
DB_PATH = "./database.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Supprimer le fichier si déjà là
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Réinitialiser et remplir la BDD
    init_db()
    with get_session() as session:
        reset_db(session)
        add_fake_data(session)

    yield
    
# Endpoint de test pour vérifier que l'API tourne bien
@app.get("/")
def read_root():
    return {"message": "API RestauSimplon fonctionne bien"}

#Pour nos futurs endpoints (routers, routes d'auth, CRUD, et
app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(delivery.router)
app.include_router(login.router)

