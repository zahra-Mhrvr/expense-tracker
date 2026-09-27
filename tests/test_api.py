def make_expense(client, **overrides):
    payload = {
        "description": "Groceries",
        "amount": 45.50,
        "category": "Food",
        "date": "2026-09-05",
    }
    payload.update(overrides)
    return client.post("/api/expenses", json=payload)


def test_create_expense(client):
    resp = make_expense(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["description"] == "Groceries"
    assert body["amount"] == 45.50
    assert "id" in body


def test_rejects_zero_or_negative_amount(client):
    resp = make_expense(client, amount=0)
    assert resp.status_code == 422

    resp2 = make_expense(client, amount=-10)
    assert resp2.status_code == 422


def test_list_expenses_filters_by_month(client):
    make_expense(client, description="September thing", date="2026-09-10")
    make_expense(client, description="August thing", date="2026-08-15")

    resp = client.get("/api/expenses?month=2026-09")
    descriptions = [e["description"] for e in resp.json()]

    assert descriptions == ["September thing"]


def test_list_expenses_filters_by_category(client):
    make_expense(client, category="Food", date="2026-09-01")
    make_expense(client, category="Transport", date="2026-09-02")

    resp = client.get("/api/expenses?category=Transport")
    categories = {e["category"] for e in resp.json()}

    assert categories == {"Transport"}


def test_delete_expense(client):
    created = make_expense(client).json()
    resp = client.delete(f"/api/expenses/{created['id']}")
    assert resp.status_code == 204

    remaining = client.get("/api/expenses").json()
    assert remaining == []


def test_delete_nonexistent_expense_returns_404(client):
    resp = client.delete("/api/expenses/999")
    assert resp.status_code == 404


def test_summary_totals_are_correct(client):
    make_expense(client, amount=30, category="Food", date="2026-09-01")
    make_expense(client, amount=20, category="Food", date="2026-09-02")
    make_expense(client, amount=50, category="Transport", date="2026-09-03")

    resp = client.get("/api/summary?month=2026-09")
    body = resp.json()

    assert body["total_spent"] == 100
    assert body["expense_count"] == 3
    by_category = {c["category"]: c["total"] for c in body["by_category"]}
    assert by_category == {"Food": 50, "Transport": 50}


def test_summary_excludes_other_months(client):
    make_expense(client, amount=30, date="2026-09-01")
    make_expense(client, amount=999, date="2026-01-01")

    resp = client.get("/api/summary?month=2026-09")
    assert resp.json()["total_spent"] == 30


def test_categories_endpoint_returns_expected_list(client):
    resp = client.get("/api/categories")
    assert "Food" in resp.json()
    assert "Other" in resp.json()


def test_index_page_is_served(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Ledger" in resp.text
