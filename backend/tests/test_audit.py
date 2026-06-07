"""Tests for the append-only audit trail."""

from tests.roles import STEWARD, SUBJECT


def test_audit_trail_records_request_actions(client):
    filed = client.post(
        "/requests",
        json={"request_type": "erasure", "subject_ref": "a@lego.dk"},
        headers=SUBJECT,
    )
    request_id = filed.json()["id"]
    client.post(f"/requests/{request_id}/approve", json={"note": "ok"}, headers=STEWARD)

    audit = client.get("/audit", headers=STEWARD)
    assert audit.status_code == 200
    actions = [event["action"] for event in audit.json()]
    assert "request.filed" in actions
    assert "request.approved" in actions


def test_audit_requires_privileged_role(client):
    assert client.get("/audit", headers=SUBJECT).status_code == 403
    assert client.get("/audit").status_code == 401
