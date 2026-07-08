from fastapi.testclient import TestClient

from app.main import app


def test_parse_endpoint_expands_rows() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/row-progression/parse",
            json={"code": "AA:CC,1=1W"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "code": "AA:CC,1=1W",
        "rows": [
            {"name": "AA", "position": 1},
            {"name": "BB", "position": 2},
            {"name": "CC", "position": 3},
            {"name": "1", "position": 4},
            {"name": "1W", "position": 4},
        ],
    }


def test_stats_endpoint_reports_counts() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/row-progression/stats",
            json={"code": "AA:CC,1=1W"},
        )

    payload = response.json()

    assert response.status_code == 200
    assert payload["total_rows"] == 5
    assert payload["unique_row_count"] == 5
    assert payload["unique_position_count"] == 4
    assert set(payload["unique_names"]) == {"AA", "BB", "CC", "1", "1W"}


def test_compress_endpoint_preserves_gaps_and_equivalents() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/row-progression/compress",
            json={
                "code": "manual",
                "rows": [
                    {"name": "A", "position": 3},
                    {"name": "B", "position": 5},
                    {"name": "BW", "position": 5},
                ],
            },
        )

    assert response.status_code == 200
    assert response.json() == {"code": "1:2!,A,4!,B=BW"}


def test_venue_diff_endpoint_has_typed_response_shape() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/row-progression/venue-diff",
            json={
                "a": {"name": "Old", "sections": {"101": "A:C"}},
                "b": {"name": "New", "sections": {"101": "A:B,D"}},
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "venue_diff": {
            "101": {
                "C": {"a": 3, "b": None},
                "D": {"a": None, "b": 3},
            }
        }
    }


def test_invalid_code_returns_400() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/row-progression/parse",
            json={"code": "A1:B1"},
        )

    assert response.status_code == 400
    assert "Ranges require matching" in response.json()["detail"]
