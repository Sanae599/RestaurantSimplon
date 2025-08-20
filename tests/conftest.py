import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

load_dotenv()
from app.db import get_session
from app.enumerations import Category, Role
from app.main import app
from app.models import User
from app.enumerations import Role
from app.security import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=True)

# Fixture setup db
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

# Fixture session test
@pytest.fixture(name="session")
def fixture_session():
    # Lier la session à la connexion partagée
    with Session(bind=connection) as session:
        yield session

# Fixture admin
@pytest.fixture
def admin_user(session):
    user = User(
        first_name="Admin", last_name="User",
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

# Fixture employe
@pytest.fixture
def employee_user(session):
    user = User(
        first_name="Employee", last_name="User",
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

# Fixture client
@pytest.fixture
def client_user(session):
    user = User(
        first_name="Client", last_name="User",
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

# Fixture client test fastapi (session SQLModel connectée à la base de test)
@pytest.fixture(name="client")
def fixture_client(session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client

# Fixture générer headers pour les tests
@pytest.fixture
def get_headers():
    return lambda user: {"Authorization": f"Bearer test_token_for_{user.role}"}

# Fixture pour override get_current_user (simule une authentification)
@pytest.fixture
def override_get_current_user(admin_user):
    from app.main import app
    from app.routers.user import get_current_user as original_get_current_user

    def _override():
        return admin_user

    app.dependency_overrides[original_get_current_user] = _override
    yield
    session.rollback()
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
