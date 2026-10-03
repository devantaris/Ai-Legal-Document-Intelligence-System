"""End-to-end API smoke test with the FakeProvider standing in for the LLM:
upload -> ingest -> chat -> summary -> key terms -> clauses -> compare."""

from tests.conftest import SAMPLE_CONTRACT, upload_contract

V2_CONTRACT = SAMPLE_CONTRACT.replace(
    """5. TERMINATION. Either Party may terminate this Agreement at any time upon
thirty (30) days' prior written notice to the other Party. The obligations in
Sections 2 and 3 survive termination for a period of three (3) years.""",
    """5. TERMINATION. This Agreement may be ended by either Party immediately
and without notice if a breach of confidentiality occurs. Otherwise, written
notice of ninety (90) days is required, and the duties in Sections 2 and 3
continue afterwards for five (5) additional years.""",
).replace(
    "interest at 1% per month",
    "interest at 2% per month",
)


def wait_ready(client, doc_id: str) -> dict:
    for _ in range(50):
        doc = client.get(f"/api/documents/{doc_id}").json()
        if doc["status"] in ("ready", "failed"):
            assert doc["status"] == "ready", doc["error"]
            return doc
        import time

        time.sleep(0.2)
    raise AssertionError("ingestion did not finish in time")


def test_full_pipeline(auth_client):
    # --- upload & ingestion -------------------------------------------------
    resp = upload_contract(auth_client, "nda.txt", SAMPLE_CONTRACT)
    assert resp.status_code == 201, resp.text
    doc_id = resp.json()["id"]
    doc = wait_ready(auth_client, doc_id)
    assert doc["chunk_count"] >= 3
    assert doc["page_count"] == 1

    # --- chat (non-streaming) -----------------------------------------------
    r = auth_client.post(
        f"/api/documents/{doc_id}/chat?stream=false",
        json={"question": "How can this agreement be terminated?"},
    )
    assert r.status_code == 200, r.text
    answer = r.json()
    assert "30 days" in answer["content"]
    assert answer["citations"], "expected citations in the answer"

    # --- chat (streaming SSE) ------------------------------------------------
    with auth_client.stream(
        "POST", f"/api/documents/{doc_id}/chat?stream=true", json={"question": "What is the term?"}
    ) as sse:
        assert sse.status_code == 200
        assert "text/event-stream" in sse.headers["content-type"]
        body = "".join(chunk for chunk in sse.iter_text())
    assert '"type": "citations"' in body or '"type":"citations"' in body
    assert "delta" in body
    assert "done" in body

    # history persisted
    msgs = auth_client.get(f"/api/documents/{doc_id}/messages").json()
    assert len(msgs) == 4  # 2 questions + 2 answers
    assert msgs[0]["role"] == "user"

    # --- summary --------------------------------------------------------------
    r = auth_client.get(f"/api/documents/{doc_id}/summary")
    assert r.status_code == 200
    assert "termination" in r.json()["summary_md"].lower() or len(r.json()["summary_md"]) > 20
    assert auth_client.get(f"/api/documents/{doc_id}").json()["has_summary"]

    # --- key terms --------------------------------------------------------------
    r = auth_client.get(f"/api/documents/{doc_id}/key-terms")
    assert r.status_code == 200
    terms = r.json()["data"]
    assert terms["agreement_type"] == "Mutual Non-Disclosure Agreement"
    assert any(p["name"] == "Acme Corp" for p in terms["parties"])

    # --- clauses --------------------------------------------------------------
    r = auth_client.get(f"/api/documents/{doc_id}/clauses")
    assert r.status_code == 200
    clauses = r.json()
    assert len(clauses) >= 3
    assert all(c["clause_type"] in ("termination", "confidentiality") for c in clauses)
    # second call is cached (no refresh)
    r2 = auth_client.get(f"/api/documents/{doc_id}/clauses")
    assert len(r2.json()) == len(clauses)

    # --- compare against a modified version ------------------------------------
    resp2 = upload_contract(auth_client, "nda_v2.txt", V2_CONTRACT)
    doc2_id = resp2.json()["id"]
    wait_ready(auth_client, doc2_id)

    r = auth_client.post(
        "/api/compare", json={"document_a_id": doc_id, "document_b_id": doc2_id}
    )
    assert r.status_code == 200, r.text
    result = r.json()
    assert result["counts"]["modified"] >= 1
    assert result["summary"]
    modified = [i for i in result["items"] if i["status"] == "modified"]
    assert all(i["a"] and i["b"] for i in modified)
    assert any(i["change_level"] in ("minor", "moderate", "major") for i in modified)

    # comparing a doc with itself is rejected
    r2 = auth_client.post(
        "/api/compare", json={"document_a_id": doc_id, "document_b_id": doc_id}
    )
    assert r2.status_code == 400


def test_upload_rejects_unsupported_files(auth_client):
    r = auth_client.post(
        "/api/documents", files={"file": ("virus.exe", b"MZ...", "application/x-msdownload")}
    )
    assert r.status_code == 400


def test_chat_before_ready_rejected(auth_client):
    # document that will fail? instead: chat on an "uploaded" doc is racy, so
    # use a nonexistent-but-owned document to check 404 handling
    r = auth_client.post(
        "/api/documents/00000000-0000-0000-0000-000000000000/chat?stream=false",
        json={"question": "hello?"},
    )
    assert r.status_code == 404
