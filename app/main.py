import os

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlmodel import Session, create_engine

from app.fake_data import add_fake_data, reset_db
from app.routers import delivery, login, order, product, user

app = FastAPI()

load_dotenv()  # charge DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

with Session(engine) as session:
    if __name__ == "__main__":
        reset_db(session)  
        add_fake_data(session)


@app.get("/")
def read_root():
    """
    Endpoint racine de l'API.

    Returns:
        dict: Message indiquant que l'API fonctionne correctement.
    """
    return {"message": "API RestauSimplon fonctionne bien"}


app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(delivery.router)
app.include_router(login.router)
