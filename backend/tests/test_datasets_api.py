"""API tests for dataset registration and lookup."""


def test_register_dataset_classifies_pii(client):
    payload = {
        "name": "crm.customers",
        "owner": "marketing-data-team",
        "source_system": "snowflake",
        "fields": [
            {"name": "email", "sample_values": ["a@lego.dk", "b@lego.dk"]},
            {"name": "cpr", "sample_values": ["010203-1234"]},
            {"name": "order_total", "sample_values": ["12.50", "9.99"]},
        ],
    }
    resp = client.post("/datasets", json=payload)
    assert resp.status_code == 201

    body = resp.json()
    assert body["contains_personal_data"] is True
    categories = {field["name"]: field["pii_category"] for field in body["fields"]}
    assert categories["email"] == "email"
    assert categories["cpr"] == "national_id"
    assert categories["order_total"] == "none"


def test_get_and_list_datasets(client):
    client.post(
        "/datasets",
        json={"name": "ds1", "owner": "o", "source_system": "s", "fields": []},
    )

    list_resp = client.get("/datasets")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    dataset_id = list_resp.json()[0]["id"]
    get_resp = client.get(f"/datasets/{dataset_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "ds1"


def test_get_missing_dataset_returns_404(client):
    assert client.get("/datasets/999").status_code == 404


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
