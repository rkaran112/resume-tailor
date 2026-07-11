from fastapi.testclient import TestClient


def test_project_crud(client: TestClient) -> None:
    resp = client.post(
        "/api/projects",
        json={
            "name": "Resume Tailor",
            "description": "A resume tailoring tool",
            "tech_tags": ["python", "react"],
            "link": "https://example.com",
            "display_order": 1,
        },
    )
    assert resp.status_code == 201
    project_id = resp.json()["id"]

    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert any(p["id"] == project_id for p in resp.json())

    resp = client.patch(f"/api/projects/{project_id}", json={"description": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated"

    resp = client.delete(f"/api/projects/{project_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/projects/{project_id}")
    assert resp.status_code == 404
