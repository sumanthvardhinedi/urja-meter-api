import respx
from httpx import Response

from app.portal.client import PortalClient


BASE_URL = "https://urja-ops.flockenergy.tech"


@respx.mock
def test_login_success():
    login_route = respx.post(f"{BASE_URL}/login").mock(
        return_value=Response(
            200,
            json={
                "type": "redirect",
                "status": 303,
                "location": "/meters",
            },
        )
    )

    client = PortalClient(
        base_url=BASE_URL,
        username="test@example.com",
        password="test-password",
    )

    try:
        client.login()

        assert login_route.called
        assert client._authenticated is True

    finally:
        client.close()


@respx.mock
def test_search_meters():
    respx.post(f"{BASE_URL}/login").mock(
        return_value=Response(
            200,
            json={
                "type": "redirect",
                "status": 303,
                "location": "/meters",
            },
        )
    )

    respx.get(
        f"{BASE_URL}/portal/meters/search",
        params={"q": "J100002", "page": "1"},
    ).mock(
        return_value=Response(
            200,
            json={
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
                "page": 1,
                "pageSize": 20,
            },
        )
    )

    client = PortalClient(
        base_url=BASE_URL,
        username="test@example.com",
        password="test-password",
    )

    try:
        result = client.search_meters("J100002", 1)

        assert result["total"] == 1
        assert result["data"][0]["meterId"] == "J100002"

    finally:
        client.close()


@respx.mock
def test_get_energy():
    respx.post(f"{BASE_URL}/login").mock(
        return_value=Response(
            200,
            json={
                "type": "redirect",
                "status": 303,
                "location": "/meters",
            },
        )
    )

    respx.get(
        f"{BASE_URL}/portal/meters/J100002/energy"
    ).mock(
        return_value=Response(
            200,
            json={
                "data": [
                    {
                        "timestamp": "23/06/2026 23:30",
                        "kwh": "6850.32",
                        "kvah": "7398.35",
                        "voltR": "227",
                    }
                ]
            },
        )
    )

    client = PortalClient(
        base_url=BASE_URL,
        username="test@example.com",
        password="test-password",
    )

    try:
        result = client.get_energy("J100002")

        assert len(result["data"]) == 1
        assert result["data"][0]["kwh"] == "6850.32"

    finally:
        client.close()


@respx.mock
def test_get_geo():
    respx.post(f"{BASE_URL}/login").mock(
        return_value=Response(
            200,
            json={
                "type": "redirect",
                "status": 303,
                "location": "/meters",
            },
        )
    )

    respx.get(
        f"{BASE_URL}/portal/meters/J100002/geo"
    ).mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "latitude": "26.840224163401967",
                    "longitude": "75.71461868999545",
                }
            },
        )
    )

    client = PortalClient(
        base_url=BASE_URL,
        username="test@example.com",
        password="test-password",
    )

    try:
        result = client.get_geo("J100002")

        assert result["data"]["latitude"] == "26.840224163401967"
        assert result["data"]["longitude"] == "75.71461868999545"

    finally:
        client.close()


@respx.mock
def test_login_failure():
    respx.post(f"{BASE_URL}/login").mock(
        return_value=Response(
            200,
            json={
                "type": "failure",
                "status": 401,
                "data": ["Invalid email or password."],
            },
        )
    )

    client = PortalClient(
        base_url=BASE_URL,
        username="wrong@example.com",
        password="wrong-password",
    )

    try:
        try:
            client.login()
            assert False, "Expected login to fail"
        except RuntimeError as exc:
            assert str(exc) == "Portal login failed"

    finally:
        client.close()