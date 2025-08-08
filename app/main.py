from fastapi import FastAPI
from db import engine, init_db, get_session
from fake_data import *
from routers import user, product, order, delivery, login

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    with get_session() as session:
        reset_db(session)
        add_fake_data(session)
    

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

