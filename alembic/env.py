import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel
from app import models
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Récupérer DATABASE_URL depuis l'environnement
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL non défini dans .env")

# Appliquer à Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Config logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadatas pour autogenerate
target_metadata = SQLModel.metadata
