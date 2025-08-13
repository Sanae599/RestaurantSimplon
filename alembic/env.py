from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel
from dotenv import load_dotenv

import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


load_dotenv()  # optionnel si tu utilises env_file

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url", "")
if not db_url:
    raise RuntimeError("Aucune DATABASE_URL trouvée (ni env, ni alembic.ini)")

config.set_main_option("sqlalchemy.url", db_url)

from app import models  # après avoir fixé sys.path
target_metadata = SQLModel.metadata
