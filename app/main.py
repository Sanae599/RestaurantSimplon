from fastapi import FastAPI
#rom app.db import engine, init_db
#rom app.models import SQLModel
#rom app.routers import user

from db import engine, init_db, get_session
from fake_data import *
from routers import user

app = FastAPI()

# Création des tables à chaque démarrage de l'app
@app.on_event("startup")
def on_startup():
    init_db()
    with get_session() as session:
            reset_db(session)
            users = create_fake_users(5)
            products = create_fake_products(10)
            deliveries = create_fake_deliveries(3)

            session.add_all(users + products + deliveries)
            session.commit()  # Pour générer les IDs

            orders = create_fake_orders(users, deliveries, 7)
            session.add_all(orders)
            session.commit()

            order_items = create_fake_order_items(orders, products)
            session.add_all(order_items)
            session.commit()
    

# Endpoint de test pour vérifier que l'API tourne bien
@app.get("/")
def read_root():
    return {"message": "API RestauSimplon fonctionne bien"}

#Pour nos futurs endpoints (routers, routes d'auth, CRUD, et
app.include_router(user.router)