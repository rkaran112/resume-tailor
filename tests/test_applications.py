from fastapi.testclient import TestClient


def _make_job_description(client: TestClient) -> int:
    resp = client.post(
        "/api/job-descriptions",
        json={"company": "Acme", "role_title": "Engineer", "raw_text": "Python engineer."},
    )
    assert resp.status_code == 201
    return int(resp.json()["id"])


def test_create_application_seeds_initial_status_event(client: TestClient) -> None:
    jd_id = _make_job_description(client)

    resp = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "applied"
    assert len(body["status_events"]) == 1
    assert body["status_events"][0]["status"] == "applied"


def test_create_application_missing_job_description_404(client: TestClient) -> None:
    resp = client.post(
        "/api/applications",
        json={
            "job_description_id": 999999,
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    )
    assert resp.status_code == 404


def test_list_and_get_application(client: TestClient) -> None:
    jd_id = _make_job_description(client)
    created = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    ).json()

    resp = client.get("/api/applications")
    assert resp.status_code == 200
    assert any(a["id"] == created["id"] for a in resp.json())

    resp = client.get(f"/api/applications/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_patch_application_updates_fields(client: TestClient) -> None:
    jd_id = _make_job_description(client)
    created = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    ).json()

    resp = client.patch(f"/api/applications/{created['id']}", json={"notes": "Referred by Sam"})
    assert resp.status_code == 200
    assert resp.json()["notes"] == "Referred by Sam"


def test_status_change_updates_status_and_appends_timeline_event(client: TestClient) -> None:
    jd_id = _make_job_description(client)
    created = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    ).json()

    resp = client.post(
        f"/api/applications/{created['id']}/status",
        json={"status": "interview", "note": "Phone screen scheduled"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "interview"
    assert len(body["status_events"]) == 2
    assert body["status_events"][1]["status"] == "interview"
    assert body["status_events"][1]["note"] == "Phone screen scheduled"

    resp = client.post(
        f"/api/applications/{created['id']}/status", json={"status": "offer"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "offer"
    assert len(body["status_events"]) == 3
    assert [e["status"] for e in body["status_events"]] == ["applied", "interview", "offer"]


def test_status_change_rejects_invalid_status(client: TestClient) -> None:
    jd_id = _make_job_description(client)
    created = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    ).json()

    resp = client.post(f"/api/applications/{created['id']}/status", json={"status": "ghosted"})
    assert resp.status_code == 422


def test_application_can_link_a_tailored_resume(client: TestClient) -> None:
    jd_id = _make_job_description(client)
    tailored_resume = client.post(
        "/api/tailored-resumes", json={"job_description_id": jd_id}
    ).json()

    resp = client.post(
        "/api/applications",
        json={
            "job_description_id": jd_id,
            "tailored_resume_id": tailored_resume["id"],
            "company": "Acme",
            "role_title": "Engineer",
            "date_applied": "2026-01-01",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["tailored_resume_id"] == tailored_resume["id"]
