import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from app import models # important pour que Alembic voie les tables

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

# Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("Aucune DATABASE_URL trouvée (ni env, ni alembic.ini)")

config.set_main_option("sqlalchemy.url", db_url)

# Import models pour target_metadata
from app import models

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """
    Exécute les migrations Alembic en mode "offline".

    Ce mode ne nécessite pas de connexion directe à la base de données. 
    Les commandes SQL sont générées et écrites sous forme de texte.

    Étapes :
        1. Configure le contexte Alembic avec l'URL de la base de données et la metadata des modèles.
        2. Active les liaisons littérales pour que les paramètres soient intégrés dans les requêtes SQL.
        3. Lance les migrations dans une transaction contextuelle.

    Raises:
        RuntimeError: Si la configuration de la base de données est incorrecte.
    """
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Exécute les migrations Alembic en mode "online".

    Ce mode utilise une connexion active à la base de données pour appliquer
    directement les modifications de schéma.

    Étapes :
        1. Crée un connectable SQLAlchemy à partir de la configuration Alembic.
        2. Établit une connexion à la base de données.
        3. Configure le contexte Alembic avec la connexion et la metadata des modèles.
        4. Exécute les migrations dans une transaction contextuelle.
    
    Raises:
        RuntimeError: Si la connexion à la base de données échoue ou la configuration est incorrecte.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
