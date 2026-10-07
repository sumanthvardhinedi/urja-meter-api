from fastapi.testclient import TestClient

from app.main import app


class FakePortalClient:
    def search_meters(self, query="", page=1):
        return {
            "data": [
                {
                    "meterId": "J100002",
                    "serialNo": "AL28136",
                    "make": "L&T",
                    "phaseType": "single",
                    "installStatus": "Installed",
                    "dtCode": "DT-003",
                }
            ],
            "total": 1,
            "page": page,
            "pageSize": 20,
        }

    def get_energy(self, meter_id):
        return {
            "data": [
                {
                    "timestamp": "23/06/2026 23:30",
                    "kwh": "6850.32",
                    "kvah": "7398.35",
                    "voltR": "227",
                }
            ]
        }

    def get_geo(self, meter_id):
        return {
            "data": {
                "latitude": "26.840224163401967",
                "longitude": "75.71461868999545",
            }
        }

    def close(self):
        pass


class FailingPortalClient:
    def search_meters(self, query="", page=1):
        raise RuntimeError("Portal unavailable")

    def get_energy(self, meter_id):
        raise RuntimeError("Portal unavailable")

    def get_geo(self, meter_id):
        raise RuntimeError("Portal unavailable")

    def close(self):
        pass


client = TestClient(app)

app.state.portal_client = FakePortalClient()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_meters():
    response = client.get(
        "/api/v1/meters",
        params={
            "search": "J100002",
            "page": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["data"][0]["meter_id"] == "J100002"
    assert body["data"][0]["serial_number"] == "AL28136"


def test_get_meter():
    response = client.get("/api/v1/meters/J100002")

    assert response.status_code == 200

    body = response.json()

    assert body["meter_id"] == "J100002"
    assert body["make"] == "L&T"


def test_get_consumption():
    response = client.get(
        "/api/v1/meters/J100002/consumption"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["meter_id"] == "J100002"
    assert body["readings"][0]["kwh"] == 6850.32
    assert body["readings"][0]["kvah"] == 7398.35
    assert body["readings"][0]["voltage_r"] == 227.0


def test_get_location():
    response = client.get(
        "/api/v1/meters/J100002/location"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["meter_id"] == "J100002"
    assert body["latitude"] == 26.840224163401967
    assert body["longitude"] == 75.71461868999545


def test_invalid_page():
    response = client.get(
        "/api/v1/meters",
        params={"page": 0},
    )

    assert response.status_code == 422


def test_meter_id_too_long():
    meter_id = "A" * 51

    response = client.get(
        f"/api/v1/meters/{meter_id}",
    )

    assert response.status_code == 422


def test_upstream_failure_returns_502():
    original_client = app.state.portal_client

    try:
        app.state.portal_client = FailingPortalClient()

        response = client.get(
            "/api/v1/meters",
            params={"search": "J100002"},
        )

        assert response.status_code == 502
        assert response.json()["detail"] == (
            "Failed to retrieve meters from upstream portal"
        )

    finally:
        app.state.portal_client = original_client