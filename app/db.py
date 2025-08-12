from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from app.config import DATABASE_URL
#DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, echo=True)

# active foreign key sqlite 
# https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
#@event.listens_for(engine, "connect")
#def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
#    cursor = dbapi_connection.cursor()
#    cursor.execute("PRAGMA foreign_keys=ON")
#    cursor.close()

def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)