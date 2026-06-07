"""Convenience auth headers for tests (mirrors the X-Actor / X-Role scheme)."""

OWNER = {"X-Actor": "alice", "X-Role": "data_owner"}
STEWARD = {"X-Actor": "sam", "X-Role": "data_steward"}
SUBJECT = {"X-Actor": "jens", "X-Role": "data_subject"}
