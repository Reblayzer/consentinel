"""Tests for role-based access control on protected endpoints."""

from tests.roles import OWNER, SUBJECT

_DATASET = {"name": "d", "owner": "o", "source_system": "s", "fields": []}


def test_register_requires_authentication(client):
    assert client.post("/datasets", json=_DATASET).status_code == 401


def test_register_forbidden_for_wrong_role(client):
    assert client.post("/datasets", json=_DATASET, headers=SUBJECT).status_code == 403


def test_register_allowed_for_owner(client):
    assert client.post("/datasets", json=_DATASET, headers=OWNER).status_code == 201


def test_unknown_role_is_rejected(client):
    headers = {"X-Actor": "x", "X-Role": "wizard"}
    assert client.post("/datasets", json=_DATASET, headers=headers).status_code == 401
