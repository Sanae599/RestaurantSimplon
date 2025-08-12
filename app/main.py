from fastapi import FastAPI
from app.db import get_session
from app.fake_data import add_fake_data, reset_db
from app.routers import user, product, order, delivery, login
from contextlib import asynccontextmanager

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API RestauSimplon fonctionne bien"}


app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(delivery.router)
app.include_router(login.router)