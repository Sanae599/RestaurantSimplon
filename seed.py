from sqlmodel import Session, create_engine
from app.fake_data import add_fake_data, reset_db  
import os
from dotenv import load_dotenv

load_dotenv()  # charge DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

with Session(engine) as session:
    reset_db(session)       # vide les tables
    add_fake_data(session)  # insère les données
