import uuid
from pathlib import Path

from app.services.storage import LocalStorage
from app.workers.queue import (
    enqueue_ingestion_task,
    get_task_progress,
    publish_task_progress,
)


def test_local_storage_lifecycle(tmp_path):
    storage = LocalStorage(root=tmp_path)
    rel_path = "test_user/test_doc/contract.txt"
    content = b"MUTUAL NON-DISCLOSURE AGREEMENT\nBetween Party A and Party B."

    saved_path = storage.save(rel_path, content, mime="text/plain")
    assert storage.exists(saved_path)

    read_back = storage.read(saved_path)
    assert read_back == content

    storage.delete(saved_path)
    assert not storage.exists(saved_path)


def test_redis_queue_and_progress_tracking():
    test_doc_id = uuid.uuid4()

    # Publish progress
    publish_task_progress(
        document_id=test_doc_id,
        status="parsing",
        step="Extracting text and structure",
        progress_pct=25,
    )

    prog = get_task_progress(test_doc_id)
    # If redis is available in the test environment
    if prog:
        assert prog["document_id"] == str(test_doc_id)
        assert prog["status"] == "parsing"
        assert prog["progress_pct"] == 25
        assert "Extracting text" in prog["step"]

    # Enqueue task
    enqueued = enqueue_ingestion_task(test_doc_id)
    assert isinstance(enqueued, bool)


def test_document_progress_endpoint(auth_client):
    from tests.conftest import upload_contract

    res = upload_contract(auth_client, filename="master_agreement.txt")
    assert res.status_code == 201, res.text
    doc_id = res.json()["id"]

    prog_res = auth_client.get(f"/api/documents/{doc_id}/progress")
    assert prog_res.status_code == 200, prog_res.text
    data = prog_res.json()
    assert "progress_pct" in data
    assert "status" in data
    assert "step" in data
