import pytest

from tests.conftest import SAMPLE_CONTRACT, upload_contract
from app.models import Chunk, Document, User
from app.core.database import SessionLocal
from app.core.security import hash_password


@pytest.fixture()
def ingested_doc(auth_client):
    """Upload the sample contract and wait for ingestion to complete."""
    resp = upload_contract(auth_client)
    assert resp.status_code == 201, resp.text
    doc_id = resp.json()["id"]
    for _ in range(50):
        doc = auth_client.get(f"/api/documents/{doc_id}").json()
        if doc["status"] in ("ready", "failed"):
            assert doc["status"] == "ready", doc["error"]
            return doc
        import time

        time.sleep(0.2)
    raise AssertionError("ingestion did not finish in time")


def _doc_model(doc_id):
    db = SessionLocal()
    try:
        return db.get(Document, doc_id)
    finally:
        db.close()


def test_chunks_have_embeddings_and_pages(ingested_doc):
    db = SessionLocal()
    try:
        chunks = (
            db.query(Chunk)
            .filter(Chunk.document_id == ingested_doc["id"])
            .order_by(Chunk.seq)
            .all()
        )
        assert len(chunks) >= 3
        assert all(c.embedding is not None for c in chunks)
        assert all(len(c.embedding) == 1024 for c in chunks)
        assert all(c.page_start == 1 for c in chunks)  # single virtual page
        assert any("termination" in c.text.lower() for c in chunks)
    finally:
        db.close()


def test_retrieval_finds_relevant_chunk(auth_client, ingested_doc):
    from app.services.retrieval import retrieve
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "lawyer@example.com").first()
        results = retrieve(db, user.id, "termination notice period", top_k=3)
        assert results
        top_text = results[0].text.lower()
        assert "termination" in top_text or "notice" in top_text
        # scoping: results belong to the user's document
        assert all(str(r.document_id) == ingested_doc["id"] for r in results)
    finally:
        db.close()


def test_documents_scoped_per_user(auth_client, client):
    """Another account must not see or query the first user's document."""
    resp = upload_contract(auth_client)
    doc_id = resp.json()["id"]

    client.post(
        "/api/auth/register", json={"email": "other@example.com", "password": "password123"}
    )
    token = client.post(
        "/api/auth/login", json={"email": "other@example.com", "password": "password123"}
    ).json()["access_token"]

    r = client.get(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404

    r2 = client.get(
        "/api/documents", headers={"Authorization": f"Bearer {token}"}
    )
    assert r2.json() == []
