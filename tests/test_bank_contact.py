from fastapi.testclient import TestClient


def test_contact_info_get_defaults_then_upsert(client: TestClient) -> None:
    resp = client.get("/api/contact-info")
    assert resp.status_code == 200
    assert resp.json()["name"] == ""

    resp = client.put(
        "/api/contact-info",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-1234",
            "location": "Remote",
            "links": [{"label": "GitHub", "url": "https://github.com/janedoe"}],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Jane Doe"
    assert resp.json()["links"] == [{"label": "GitHub", "url": "https://github.com/janedoe"}]

    resp = client.get("/api/contact-info")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Jane Doe"
