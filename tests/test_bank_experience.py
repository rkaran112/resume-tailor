from fastapi.testclient import TestClient


def test_experience_entry_crud(client: TestClient) -> None:
    resp = client.post(
        "/api/experience-entries",
        json={
            "company": "Acme Corp",
            "title": "Software Engineer",
            "location": "Remote",
            "start_date": "2022-01-01",
            "end_date": None,
            "display_order": 1,
        },
    )
    assert resp.status_code == 201
    entry_id = resp.json()["id"]

    resp = client.get("/api/experience-entries")
    assert resp.status_code == 200
    assert any(e["id"] == entry_id for e in resp.json())

    resp = client.patch(f"/api/experience-entries/{entry_id}", json={"title": "Senior Engineer"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Senior Engineer"

    resp = client.delete(f"/api/experience-entries/{entry_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/experience-entries/{entry_id}")
    assert resp.status_code == 404
