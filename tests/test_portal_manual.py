import pytest

from app.config import settings
from app.portal.client import PortalClient


@pytest.mark.integration
def test_portal_connection():
    client = PortalClient(
        base_url=settings.urja_base_url,
        username=settings.urja_username,
        password=settings.urja_password,
    )

    try:
        client.login()

        meters = client.search_meters(
            query="J100002",
            page=1,
        )

        assert meters["total"] == 1
        assert meters["data"][0]["meterId"] == "J100002"

        energy = client.get_energy("J100002")

        assert "data" in energy
        assert len(energy["data"]) > 0

        geo = client.get_geo("J100002")

        assert "data" in geo
        assert "latitude" in geo["data"]
        assert "longitude" in geo["data"]

    finally:
        client.close()