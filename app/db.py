import os

from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini. A configurer dans le dans .env")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)

