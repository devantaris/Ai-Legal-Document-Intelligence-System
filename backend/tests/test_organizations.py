import uuid
from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, password: str = "StrongPass123!") -> str:
    res = client.post("/api/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201, res.text
    return res.json()["access_token"]


def test_auto_provision_organization_and_list(client):
    token = _register(client, f"lawyer_{uuid.uuid4().hex[:6]}@lawfirm.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/organizations", headers=headers)
    assert res.status_code == 200, res.text
    orgs = res.json()
    assert len(orgs) >= 1
    primary_org = orgs[0]
    assert primary_org["role"] == "owner"
    assert primary_org["plan_tier"] == "sovereign_pro"
    assert primary_org["workspace_count"] >= 1


def test_create_organization_and_workspaces(client):
    token = _register(client, f"general_counsel_{uuid.uuid4().hex[:6]}@enterprise.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create new org
    res = client.post(
        "/api/organizations",
        json={"name": "Acme Global Legal"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    new_org = res.json()
    assert new_org["name"] == "Acme Global Legal"
    assert new_org["role"] == "owner"
    org_id = new_org["id"]

    # List workspaces in new org
    res = client.get(f"/api/organizations/{org_id}/workspaces", headers=headers)
    assert res.status_code == 200, res.text
    workspaces = res.json()
    assert len(workspaces) == 1
    assert workspaces[0]["name"] == "General Matters"

    # Create a specialized workspace (e.g. M&A Deal)
    res = client.post(
        f"/api/organizations/{org_id}/workspaces",
        json={"name": "Project Apollo M&A Due Diligence", "description": "Strict confidential acquisition files"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    ws = res.json()
    assert ws["name"] == "Project Apollo M&A Due Diligence"


def test_invite_member_and_rbac(client):
    owner_token = _register(client, f"senior_partner_{uuid.uuid4().hex[:6]}@firm.com")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Get primary org
    res = client.get("/api/organizations", headers=owner_headers)
    org_id = res.json()[0]["id"]

    # Invite a junior reviewer
    reviewer_email = f"paralegal_{uuid.uuid4().hex[:6]}@firm.com"
    res = client.post(
        f"/api/organizations/{org_id}/members",
        json={"email": reviewer_email, "role": "reviewer"},
        headers=owner_headers,
    )
    assert res.status_code == 201, res.text
    reviewer_member = res.json()
    assert reviewer_member["email"] == reviewer_email
    assert reviewer_member["role"] == "reviewer"

    # Update role to counsel
    res = client.patch(
        f"/api/organizations/{org_id}/members/{reviewer_member['user_id']}",
        json={"role": "counsel"},
        headers=owner_headers,
    )
    assert res.status_code == 200, res.text
    assert res.json()["role"] == "counsel"


def test_organization_usage_endpoint(client):
    token = _register(client, f"gc_{uuid.uuid4().hex[:6]}@techcorp.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/organizations", headers=headers)
    org_id = res.json()[0]["id"]

    res = client.get(f"/api/organizations/{org_id}/usage", headers=headers)
    assert res.status_code == 200, res.text
    usage = res.json()
    assert usage["sovereign_inference"] is True
    assert usage["members_count"] >= 1
    assert usage["workspaces_count"] >= 1
    assert len(usage["features"]) >= 4
