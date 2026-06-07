"""Heuristic PII classifier — the data-engineering core of Consentinel.

Given a column name and a sample of its values, infer whether the column holds
personal data and which GDPR-relevant category it belongs to. Two weak signals
are combined into a confidence score:

* **value signal** — the fraction of sampled values matching a category's
  regex / validator (e.g. a valid email address, or a Luhn-valid card number);
* **name signal** — whether the column name contains a known keyword. Keywords
  are multilingual (English + Danish) because the LEGO Group is based in
  Denmark, so source columns are often named ``fornavn``, ``adresse``, ``cpr``…

The module is deliberately dependency-free and deterministic, so it is trivial
to unit-test and to run as a batch step over many datasets.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from app.domain.enums import PIICategory

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
IP_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
PHONE_RE = re.compile(r"^\+?\d[\d\s().-]{6,}\d$")
# Danish CPR (national identification number): DDMMYY-SSSS, hyphen optional.
CPR_RE = re.compile(r"^\d{6}-?\d{4}$")
DOB_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{2}[/.]\d{2}[/.]\d{4}$")
CARD_RE = re.compile(r"^\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}$")

# Column-name keywords (substring match against the lowercased name).
NAME_HINTS: dict[PIICategory, tuple[str, ...]] = {
    PIICategory.EMAIL: ("email", "e-mail", "mail"),
    PIICategory.PHONE: ("phone", "mobile", "telefon", "mobil", "tlf"),
    PIICategory.NAME: ("name", "navn", "fornavn", "efternavn"),
    PIICategory.NATIONAL_ID: ("cpr", "ssn", "national_id", "nationalid", "personnummer"),
    PIICategory.ADDRESS: ("address", "adresse", "street", "postnr", "postal", "zip"),
    PIICategory.DATE_OF_BIRTH: ("dob", "birth", "born", "fodsel", "foedsel"),
    PIICategory.IP_ADDRESS: ("ip", "ip_address", "ipaddr"),
    PIICategory.CREDIT_CARD: ("card", "creditcard", "cc_number", "pan"),
}


def _luhn_ok(value: str) -> bool:
    """Validate a candidate card number with the Luhn checksum."""
    digits = [int(c) for c in re.sub(r"\D", "", value)]
    if len(digits) < 13:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


# Validators for categories whose values have a recognisable shape.
VALUE_MATCHERS: dict[PIICategory, Callable[[str], bool]] = {
    PIICategory.EMAIL: lambda v: bool(EMAIL_RE.match(v)),
    PIICategory.NATIONAL_ID: lambda v: bool(CPR_RE.match(v)),
    PIICategory.CREDIT_CARD: lambda v: bool(CARD_RE.match(v)) and _luhn_ok(v),
    PIICategory.IP_ADDRESS: lambda v: bool(IP_RE.match(v))
    and all(0 <= int(octet) <= 255 for octet in v.split(".")),
    PIICategory.DATE_OF_BIRTH: lambda v: bool(DOB_RE.match(v)),
    PIICategory.PHONE: lambda v: bool(PHONE_RE.match(v)),
}

# Most-specific categories are tested first so, e.g., a CPR number is not
# mistaken for a phone number (both are runs of digits).
_VALUE_PRIORITY: tuple[PIICategory, ...] = (
    PIICategory.EMAIL,
    PIICategory.NATIONAL_ID,
    PIICategory.CREDIT_CARD,
    PIICategory.IP_ADDRESS,
    PIICategory.DATE_OF_BIRTH,
    PIICategory.PHONE,
)


@dataclass(frozen=True)
class Classification:
    category: PIICategory
    confidence: float  # 0.0 – 1.0
    rationale: str

    @property
    def is_personal_data(self) -> bool:
        return self.category != PIICategory.NONE


def _name_hint(column_name: str) -> PIICategory | None:
    low = column_name.strip().lower()
    for category, keywords in NAME_HINTS.items():
        if any(keyword in low for keyword in keywords):
            return category
    return None


def _value_score(category: PIICategory, values: list[str]) -> float:
    matcher = VALUE_MATCHERS.get(category)
    if matcher is None or not values:
        return 0.0
    return sum(1 for value in values if matcher(value)) / len(values)


def classify_field(column_name: str, sample_values: list[str] | None = None) -> Classification:
    """Classify a single column from its name and a sample of its values."""
    values = [v.strip() for v in (sample_values or []) if v and v.strip()]
    name_hint = _name_hint(column_name)

    # Strongest value-based signal across all categories with a validator.
    best_category = PIICategory.NONE
    best_score = 0.0
    for category in _VALUE_PRIORITY:
        score = _value_score(category, values)
        if score > best_score:
            best_category, best_score = category, score

    # A clear value signal wins; a matching name nudges confidence up.
    if best_score >= 0.5:
        confidence = best_score
        rationale = f"{best_score:.0%} of sampled values match the {best_category.value} pattern"
        if name_hint == best_category:
            confidence = min(1.0, confidence + 0.15)
            rationale += f"; column name also indicates {best_category.value}"
        return Classification(best_category, round(confidence, 2), rationale)

    # No strong values, but the name is telling (covers NAME / ADDRESS, which
    # have no reliable value pattern).
    if name_hint is not None:
        return Classification(
            name_hint,
            0.6,
            f"column name '{column_name}' matches a known {name_hint.value} keyword",
        )

    # A weak value signal with no name support — flag it, but low-confidence.
    if best_score > 0.0:
        return Classification(
            best_category,
            round(best_score, 2),
            f"only {best_score:.0%} of values match {best_category.value}; low confidence",
        )

    return Classification(PIICategory.NONE, 1.0, "no PII signal in column name or sampled values")
