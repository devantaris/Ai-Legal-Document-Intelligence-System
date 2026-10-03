import os

from app.core.config import get_settings

# Point the whole app at a dedicated test database BEFORE importing any module
# that creates the engine, so dev data is never touched by tests.
TEST_DB_NAME = "legal_ai_test"
_probe = get_settings()
if not _probe.DATABASE_URL.endswith(f"/{TEST_DB_NAME}"):
    os.environ["DATABASE_URL"] = (
        _probe.DATABASE_URL.rsplit("/", 1)[0] + f"/{TEST_DB_NAME}"
    )
    get_settings.cache_clear()
    import app.core.config as _config_module

    _config_module.settings = get_settings()  # rebind for later imports

import sqlalchemy as sa
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.deps import get_db
from app.main import app


def _create_test_database() -> None:
    admin_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    admin = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            exists = conn.execute(
                sa.text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": TEST_DB_NAME},
            ).scalar()
            if not exists:
                conn.execute(sa.text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
        # pgvector must be enabled per-database before create_all runs
        with engine.connect() as conn:
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    except sa.exc.SQLAlchemyError:
        pass  # server unreachable: individual tests will surface the error
    finally:
        admin.dispose()


_create_test_database()

# every module that holds its own `get_provider` binding
PROVIDER_MODULES = [
    "app.services.ingestion",
    "app.services.retrieval",
    "app.services.chat",
    "app.services.summarization",
    "app.services.key_terms",
    "app.services.clauses",
    "app.services.compare",
]

SAMPLE_CONTRACT = """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement (the "Agreement") is entered into as of
January 1, 2024 (the "Effective Date"), by and between Acme Corp, a Delaware
corporation ("Company"), and Beta LLC, a New York limited liability company
("Recipient"), each a "Party" and together the "Parties".

1. PURPOSE. The Parties wish to explore a business relationship and may
disclose certain confidential information to one another in connection with
that purpose.

2. CONFIDENTIAL INFORMATION. "Confidential Information" means any non-public
information disclosed by one Party to the other, whether oral, written or
electronic, that is designated as confidential or that reasonably should be
understood to be confidential given the nature of the information and the
circumstances of disclosure.

3. OBLIGATIONS OF THE RECIPIENT. The Recipient shall:
3.1 protect the Confidential Information with at least the same degree of
care it uses to protect its own confidential information; and
3.2 not disclose the Confidential Information to any third party without the
prior written consent of the disclosing Party; and
3.3 use the Confidential Information solely for the Purpose stated above.

4. TERM. This Agreement commences on the Effective Date and continues for a
period of two (2) years, unless terminated earlier in accordance with
Section 5.

5. TERMINATION. Either Party may terminate this Agreement at any time upon
thirty (30) days' prior written notice to the other Party. The obligations in
Sections 2 and 3 survive termination for a period of three (3) years.

6. GOVERNING LAW. This Agreement is governed by the laws of the State of
Delaware, without regard to its conflict of laws principles.

7. DISPUTE RESOLUTION. Any dispute arising out of or relating to this
Agreement shall be finally resolved by binding arbitration administered in
New York, New York.

8. MISCELLANEOUS. This Agreement constitutes the entire agreement between the
Parties with respect to its subject matter and may be amended only in writing
signed by both Parties.
"""


@pytest.fixture()
def fake_provider(monkeypatch):
    from tests.fakes import FakeProvider

    fake = FakeProvider()
    for mod in PROVIDER_MODULES:
        monkeypatch.setattr(f"{mod}.get_provider", lambda fake=fake: fake)
    return fake


@pytest.fixture()
def client(fake_provider):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "lawyer@example.com", "password": "password123"},
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def upload_contract(client, filename: str = "nda.txt", text: str = SAMPLE_CONTRACT):
    return client.post(
        "/api/documents",
        files={"file": (filename, text.encode(), "text/plain")},
    )
