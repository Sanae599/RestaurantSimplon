from fastapi import FastAPI
from app.db import get_session
from app.fake_data import add_fake_data, reset_db  
from app.routers import user, product, order, delivery, login
from contextlib import asynccontextmanager
from sqlmodel import Session, create_engine
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()  # charge DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

with Session(engine) as session:
    if __name__ == "__main__":
        reset_db(session)       # vide les tables
        add_fake_data(session)  # insère les données

@app.get("/")
def read_root():
    return {"message": "API RestauSimplon fonctionne bien"}

app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(delivery.router)
app.include_router(login.router)
