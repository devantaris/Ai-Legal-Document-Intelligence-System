import uuid
from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, password: str = "StrongPass123!") -> tuple[str, str]:
    res = client.post("/api/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    orgs = client.get("/api/organizations", headers=headers).json()
    return token, orgs[0]["id"]


def test_list_and_create_playbooks(client: TestClient):
    token, org_id = _register(client, f"gc_{uuid.uuid4().hex[:6]}@lawcorp.com")
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    # 1. Listing should auto-seed Institutional Commercial Standard
    res = client.get("/api/playbooks", headers=headers)
    assert res.status_code == 200, res.text
    playbooks = res.json()
    assert len(playbooks) >= 1
    assert playbooks[0]["name"] == "Institutional Commercial Standard"
    assert playbooks[0]["is_default"] is True
    assert playbooks[0]["rule_count"] >= 10

    # 2. Create custom playbook
    res = client.post(
        "/api/playbooks",
        json={
            "name": "Aggressive Vendor SaaS Playbook",
            "description": "Strict compliance thresholds for all supplier contracts",
            "is_default": False,
            "rules": {
                "limitation_of_liability": {
                    "clause_type": "limitation_of_liability",
                    "name": "Limitation of Liability",
                    "preferred_position": "Aggregate cap limited strictly to fees paid in previous 12 months.",
                    "unacceptable_triggers": ["unlimited liability", "zero liability"],
                    "guidance": "Reject all uncapped liability for general breach.",
                }
            },
        },
        headers=headers,
    )
    assert res.status_code == 201, res.text
    new_pb = res.json()
    assert new_pb["name"] == "Aggressive Vendor SaaS Playbook"
    assert new_pb["rule_count"] == 1
    pb_id = new_pb["id"]

    # 3. Update playbook
    res = client.patch(
        f"/api/playbooks/{pb_id}",
        json={"name": "Aggressive Vendor SaaS Playbook (Revised)"},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    assert res.json()["name"] == "Aggressive Vendor SaaS Playbook (Revised)"

    # 4. Delete custom playbook
    res = client.delete(f"/api/playbooks/{pb_id}", headers=headers)
    assert res.status_code == 204, res.text


def test_audit_logs_and_export_csv(client: TestClient):
    token, org_id = _register(client, f"compliance_officer_{uuid.uuid4().hex[:6]}@enterprise.com")
    headers = {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

    # Trigger some operations to generate audit logs
    client.get("/api/playbooks", headers=headers)

    # Fetch audit logs
    res = client.get(f"/api/organizations/{org_id}/audit-logs", headers=headers)
    assert res.status_code == 200, res.text
    logs = res.json()
    assert isinstance(logs, list)

    # Export audit logs CSV
    csv_res = client.get(f"/api/organizations/{org_id}/audit-logs/export-csv", headers=headers)
    assert csv_res.status_code == 200, csv_res.text
    assert "Timestamp (UTC)" in csv_res.text
    assert "Actor Email" in csv_res.text
    assert "Action" in csv_res.text
