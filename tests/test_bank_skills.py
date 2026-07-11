from fastapi.testclient import TestClient


def test_skill_crud(client: TestClient) -> None:
    resp = client.post(
        "/api/skills", json={"name": "Python", "category": "language", "tags": ["backend"]}
    )
    assert resp.status_code == 201
    skill_id = resp.json()["id"]

    resp = client.get("/api/skills")
    assert resp.status_code == 200
    assert any(s["id"] == skill_id for s in resp.json())

    resp = client.get(f"/api/skills/{skill_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python"

    resp = client.patch(f"/api/skills/{skill_id}", json={"category": "tool"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "tool"
    assert resp.json()["name"] == "Python"

    resp = client.delete(f"/api/skills/{skill_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/skills/{skill_id}")
    assert resp.status_code == 404


def test_get_missing_skill_404(client: TestClient) -> None:
    resp = client.get("/api/skills/999999")
    assert resp.status_code == 404
