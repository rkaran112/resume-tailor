from fastapi.testclient import TestClient


def _make_experience_entry(client: TestClient) -> int:
    resp = client.post(
        "/api/experience-entries",
        json={
            "company": "Acme Corp",
            "title": "Engineer",
            "location": "Remote",
            "start_date": "2022-01-01",
        },
    )
    assert resp.status_code == 201
    return int(resp.json()["id"])


def _make_project(client: TestClient) -> int:
    resp = client.post(
        "/api/projects",
        json={"name": "Side Project", "description": "desc"},
    )
    assert resp.status_code == 201
    return int(resp.json()["id"])


def test_bullet_crud_for_experience_entry(client: TestClient) -> None:
    entry_id = _make_experience_entry(client)

    resp = client.post(
        "/api/bullets",
        json={
            "experience_entry_id": entry_id,
            "text": "Shipped feature X",
            "tags": ["backend"],
            "impact_metric": "20% faster",
        },
    )
    assert resp.status_code == 201
    bullet_id = resp.json()["id"]
    assert resp.json()["project_id"] is None

    resp = client.patch(f"/api/bullets/{bullet_id}", json={"text": "Shipped feature Y"})
    assert resp.status_code == 200
    assert resp.json()["text"] == "Shipped feature Y"

    resp = client.delete(f"/api/bullets/{bullet_id}")
    assert resp.status_code == 204


def test_bullet_crud_for_project(client: TestClient) -> None:
    project_id = _make_project(client)

    resp = client.post(
        "/api/bullets",
        json={"project_id": project_id, "text": "Built the thing"},
    )
    assert resp.status_code == 201
    assert resp.json()["experience_entry_id"] is None


def test_bullet_requires_exactly_one_parent_neither_set(client: TestClient) -> None:
    resp = client.post("/api/bullets", json={"text": "Orphan bullet"})
    assert resp.status_code == 422


def test_bullet_requires_exactly_one_parent_both_set(client: TestClient) -> None:
    entry_id = _make_experience_entry(client)
    project_id = _make_project(client)

    resp = client.post(
        "/api/bullets",
        json={
            "experience_entry_id": entry_id,
            "project_id": project_id,
            "text": "Ambiguous bullet",
        },
    )
    assert resp.status_code == 422


def test_bullet_patch_cannot_clear_only_parent(client: TestClient) -> None:
    entry_id = _make_experience_entry(client)
    resp = client.post(
        "/api/bullets", json={"experience_entry_id": entry_id, "text": "Some bullet"}
    )
    bullet_id = resp.json()["id"]

    resp = client.patch(f"/api/bullets/{bullet_id}", json={"experience_entry_id": None})
    assert resp.status_code == 422
