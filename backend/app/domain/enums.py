"""Domain enumerations shared across the data model and the API layer.

Kept in one place so the GDPR vocabulary (legal bases, request types, governance
roles, PII categories) stays consistent between the classifier, the ORM, and the
JSON contract.
"""

from enum import StrEnum


class PIICategory(StrEnum):
    """Category of personal data a column may contain."""

    NONE = "none"
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    NATIONAL_ID = "national_id"  # e.g. Danish CPR number, US SSN
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    IP_ADDRESS = "ip_address"
    CREDIT_CARD = "credit_card"


class LegalBasis(StrEnum):
    """Lawful basis for processing under GDPR Article 6."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class Role(StrEnum):
    """Governance roles used for access decisions."""

    ADMIN = "admin"
    DATA_OWNER = "data_owner"
    DATA_STEWARD = "data_steward"
    DATA_SUBJECT = "data_subject"


class RequestType(StrEnum):
    """Type of data-subject request."""

    ACCESS = "access"  # GDPR Art. 15 — right of access
    ERASURE = "erasure"  # GDPR Art. 17 — right to be forgotten


class RequestStatus(StrEnum):
    """Lifecycle state of a compliance request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
