"""Tests for the compliance-request approval workflow."""

from tests.roles import STEWARD, SUBJECT


def _file_erasure(client, subject_ref="jens@lego.dk") -> int:
    resp = client.post(
        "/requests",
        json={"request_type": "erasure", "subject_ref": subject_ref, "reason": "delete me"},
        headers=SUBJECT,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"
    return resp.json()["id"]


def test_full_erasure_workflow(client):
    request_id = _file_erasure(client)

    approved = client.post(
        f"/requests/{request_id}/approve", json={"note": "identity verified"}, headers=STEWARD
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["decided_by"] == "sam"

    completed = client.post(f"/requests/{request_id}/complete", json={}, headers=STEWARD)
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["resolved_at"] is not None


def test_cannot_complete_before_approval(client):
    request_id = _file_erasure(client)
    # completing a still-pending request is a 409 conflict
    resp = client.post(f"/requests/{request_id}/complete", json={}, headers=STEWARD)
    assert resp.status_code == 409


def test_reject_is_terminal(client):
    request_id = _file_erasure(client)
    rejected = client.post(
        f"/requests/{request_id}/reject", json={"note": "could not verify"}, headers=STEWARD
    )
    assert rejected.json()["status"] == "rejected"
    # a rejected request can no longer be approved
    resp = client.post(f"/requests/{request_id}/approve", json={}, headers=STEWARD)
    assert resp.status_code == 409


def test_subject_cannot_approve_own_request(client):
    request_id = _file_erasure(client)
    resp = client.post(f"/requests/{request_id}/approve", json={}, headers=SUBJECT)
    assert resp.status_code == 403


def test_filter_requests_by_status(client):
    pending_id = _file_erasure(client, "a@lego.dk")
    resolved_id = _file_erasure(client, "b@lego.dk")
    client.post(f"/requests/{resolved_id}/reject", json={}, headers=STEWARD)

    pending = client.get("/requests", params={"status": "pending"})
    assert pending.status_code == 200
    ids = [r["id"] for r in pending.json()]
    assert pending_id in ids
    assert resolved_id not in ids
