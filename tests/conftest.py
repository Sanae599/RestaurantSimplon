import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()
from app.db import get_session
from app.enumerations import Category, Role
from app.main import app
from app.models import Product, User
from app.security import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)
# Connection partagée
connection = engine.connect()
SQLModel.metadata.create_all(connection)

@pytest.fixture(name="session")
def fixture_session():
    """
    Fournit une session SQLModel liée à la base de données de test en mémoire.

    Utilisation :
        - Toutes les interactions avec la base de données dans les tests utilisent cette session.
    
    Yield :
        - Une instance de Session SQLModel.
    """
    with Session(bind=connection) as session:
        yield session


# Fixtures utilisateurs
@pytest.fixture
def admin_user(session):
    """
    Crée et retourne un utilisateur avec le rôle ADMIN pour les tests.

    Étapes :
        1. Instancie un utilisateur avec rôle ADMIN et mot de passe hashé.
        2. Ajoute l'utilisateur à la session et commit.
        3. Rafraîchit l'objet pour obtenir l'ID.
    
    Yield :
        - L'utilisateur ADMIN créé.
    """
    user = User(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        role=Role.ADMIN,
        password_hashed=hash_password("secret123"),
        address_user="123 Admin Street",
        phone="0000000000",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user


@pytest.fixture
def employee_user(session):
    """
    Crée et retourne un utilisateur avec le rôle EMPLOYEE pour les tests.

    Étapes :
        1. Instancie un utilisateur avec rôle EMPLOYEE et mot de passe hashé.
        2. Ajoute l'utilisateur à la session et commit.
        3. Rafraîchit l'objet pour obtenir l'ID.

    Yield :
        - L'utilisateur EMPLOYEE créé.
    """
    user = User(
        first_name="Employee",
        last_name="User",
        email="employee@example.com",
        role=Role.EMPLOYEE,
        password_hashed=hash_password("secret123"),
        address_user="456 Employee Street",
        phone="0111111111",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user


@pytest.fixture
def client_user(session):
    """
    Crée et retourne un utilisateur avec le rôle CLIENT pour les tests.

    Étapes :
        1. Instancie un utilisateur avec rôle CLIENT et mot de passe hashé.
        2. Ajoute l'utilisateur à la session et commit.
        3. Rafraîchit l'objet pour obtenir l'ID.

    Yield :
        - L'utilisateur CLIENT créé.
    """
    user = User(
        first_name="Client",
        last_name="User",
        email="client@example.com",
        role=Role.CLIENT,
        password_hashed=hash_password("secret123"),
        address_user="789 Client Street",
        phone="0222222222",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user


# Fixture client FastAPI
@pytest.fixture(name="client")
def fixture_client(session):
    """
    Fournit un client FastAPI configuré pour utiliser la session de test.

    Étapes :
        1. Redéfinit la dépendance get_session pour renvoyer la session de test.
        2. Crée un TestClient pour l'application FastAPI.
    
    Yield :
        - Une instance de TestClient pour envoyer des requêtes HTTP aux routes.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client


# Override get_current_user
@pytest.fixture
def override_get_current_admin(admin_user):
    """
    Override la dépendance get_current_user pour retourner l'ADMIN.

    Utilisation :
        - Permet de simuler qu'un utilisateur ADMIN est connecté lors des tests.

    Yield :
        - Aucun objet, juste l'override actif pendant le test.
    """
    from app.routers.user import get_current_user as original

    app.dependency_overrides[original] = lambda: admin_user
    yield
    app.dependency_overrides.pop(original)


@pytest.fixture
def override_get_current_employee(employee_user):
    """
    Override la dépendance get_current_user pour retourner l'EMPLOYEE.

    Utilisation :
        - Permet de simuler qu'un utilisateur EMPLOYEE est connecté lors des tests.

    Yield :
        - Aucun objet, juste l'override actif pendant le test.
    """

    from app.routers.user import get_current_user as original

    app.dependency_overrides[original] = lambda: employee_user
    yield
    app.dependency_overrides.pop(original)


@pytest.fixture
def override_get_current_client(client_user):
    """
    Override la dépendance get_current_user pour retourner le CLIENT.

    Utilisation :
        - Permet de simuler qu'un utilisateur CLIENT est connecté lors des tests.

    Yield :
        - Aucun objet, juste l'override actif pendant le test.
    """
    from app.routers.user import get_current_user as original

    app.dependency_overrides[original] = lambda: client_user
    yield
    app.dependency_overrides.pop(original)


# Fixture produit
@pytest.fixture
def produit(session):
    """
    Crée et retourne un produit pour les tests.

    Étapes :
        1. Instancie un produit avec nom, prix, catégorie, description et stock.
        2. Ajoute le produit à la session et commit.
        3. Rafraîchit l'objet pour obtenir l'ID.

    Yield :
        - Le produit créé.
    """
    produit = Product(
        name="Produit Test",
        unit_price=10.0,
        category=Category.PLAT_PRINCIPAL,
        description="Description du produit test",
        stock=100,
    )
    session.add(produit)
    session.commit()
    session.refresh(produit)
    yield produit


# Nettoyage après chaque test
@pytest.fixture(autouse=True)
def clean_db(session):
    """
    Nettoie la base de données après chaque test.

    Étapes :
        1. Effectue un rollback pour annuler les modifications non commit.
        2. Supprime toutes les lignes de toutes les tables.
        3. Commit pour appliquer le nettoyage.

    Utilisation :
        - Fixture autouse=True, donc exécutée automatiquement pour chaque test.
    """
    yield
    session.rollback()
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
