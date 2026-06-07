"""Tests for usage agreements (lawful basis + retention)."""

from tests.roles import OWNER


def _make_dataset(client) -> int:
    resp = client.post(
        "/datasets",
        json={"name": "crm", "owner": "o", "source_system": "s", "fields": []},
        headers=OWNER,
    )
    return resp.json()["id"]


def test_add_and_list_agreement(client):
    dataset_id = _make_dataset(client)
    resp = client.post(
        f"/datasets/{dataset_id}/agreements",
        json={"purpose": "marketing analytics", "legal_basis": "consent", "retention_days": 365},
        headers=OWNER,
    )
    assert resp.status_code == 201
    assert resp.json()["legal_basis"] == "consent"

    listing = client.get(f"/datasets/{dataset_id}/agreements")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_agreement_on_missing_dataset_returns_404(client):
    resp = client.post(
        "/datasets/999/agreements",
        json={"purpose": "p", "legal_basis": "consent", "retention_days": 30},
        headers=OWNER,
    )
    assert resp.status_code == 404


def test_retention_must_be_positive(client):
    dataset_id = _make_dataset(client)
    resp = client.post(
        f"/datasets/{dataset_id}/agreements",
        json={"purpose": "p", "legal_basis": "consent", "retention_days": 0},
        headers=OWNER,
    )
    assert resp.status_code == 422  # validation error
