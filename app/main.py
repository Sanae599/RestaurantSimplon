from fastapi import FastAPI
from app.db import engine, init_db
from app.models import SQLModel

app = FastAPI()

# Création des tables à chaque démarrage de l'app
@app.on_event("startup")
def on_startup():
    init_db()

# Endpoint de test pour vérifier que l'API tourne bien
@app.get("/")
def read_root():
    return {"message": "API RestauSimplon fonctionne bien"}

#Pour nos futurs endpoints (routers, routes d'auth, CRUD, etc.)
