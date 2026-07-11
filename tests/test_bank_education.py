from fastapi.testclient import TestClient


def test_education_entry_crud(client: TestClient) -> None:
    resp = client.post(
        "/api/education-entries",
        json={
            "institution": "State University",
            "degree": "B.S.",
            "field": "Computer Science",
            "start_date": "2018-09-01",
            "end_date": "2022-05-01",
            "gpa": "3.8",
        },
    )
    assert resp.status_code == 201
    entry_id = resp.json()["id"]

    resp = client.get("/api/education-entries")
    assert resp.status_code == 200
    assert any(e["id"] == entry_id for e in resp.json())

    resp = client.patch(f"/api/education-entries/{entry_id}", json={"gpa": "3.9"})
    assert resp.status_code == 200
    assert resp.json()["gpa"] == "3.9"

    resp = client.delete(f"/api/education-entries/{entry_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/education-entries/{entry_id}")
    assert resp.status_code == 404
