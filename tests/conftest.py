import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv
from dotenv import load_dotenv

load_dotenv()
load_dotenv()
from app.db import get_session
from app.main import app
from app.models import User, Product
from app.enumerations import Role, Category
from app.security import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)
# Connection partagée
connection = engine.connect()
SQLModel.metadata.create_all(connection)

# Session pour les tests
@pytest.fixture(name="session")
def fixture_session():
    # Lier la session à la connexion partagée
    with Session(bind=connection) as session:
        yield session

# Fixtures utilisateurs
@pytest.fixture
def admin_user(session):
    user = User(
        first_name="Admin", last_name="User",
        email="admin@example.com",
        role=Role.ADMIN,
        password_hashed=hash_password("secret123"),
        address_user="123 Admin Street",
        phone="0000000000"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user

@pytest.fixture
def employee_user(session):
    user = User(
        first_name="Employee", last_name="User",
        email="employee@example.com",
        role=Role.EMPLOYEE,
        password_hashed=hash_password("secret123"),
        address_user="456 Employee Street",
        phone="1111111111"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user

@pytest.fixture
def client_user(session):
    user = User(
        first_name="Client", last_name="User",
        email="client@example.com",
        role=Role.CLIENT,
        password_hashed=hash_password("secret123"),
        address_user="789 Client Street",
        phone="2222222222"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user

# Fixture client FastAPI
@pytest.fixture(name="client")
def fixture_client(session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client

# Override get_current_user
@pytest.fixture
def override_get_current_admin(admin_user):
    from app.routers.user import get_current_user as original
    app.dependency_overrides[original] = lambda: admin_user
    yield
    app.dependency_overrides.pop(original)

@pytest.fixture
def override_get_current_employee(employee_user):
    from app.routers.user import get_current_user as original
    app.dependency_overrides[original] = lambda: employee_user
    yield
    app.dependency_overrides.pop(original)

@pytest.fixture
def override_get_current_client(client_user):
    from app.routers.user import get_current_user as original
    app.dependency_overrides[original] = lambda: client_user
    yield
    app.dependency_overrides.pop(original)

# Fixture produit
@pytest.fixture
def produit(session):
    produit = Product(
        name="Produit Test",
        unit_price=10.0,
        category=Category.PLAT_PRINCIPAL,
        description="Description du produit test",
        stock=100
    )
    session.add(produit)
    session.commit()
    session.refresh(produit)
    yield produit

# Nettoyage après chaque test
@pytest.fixture(autouse=True)
def clean_db(session):
    yield
    session.rollback()
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()