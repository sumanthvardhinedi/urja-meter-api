from typing import Any

import httpx


class PortalClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=False,
        )

        self._authenticated = False

    def login(self) -> None:
        response = self.client.post(
            "/login",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": self.base_url,
                "Referer": f"{self.base_url}/login",
                "X-SvelteKit-Action": "true",
            },
            data={
                "email": self.username,
                "password": self.password,
            },
        )

        response.raise_for_status()

        body = response.json()

        if body.get("type") == "failure":
            raise RuntimeError("Portal login failed")

        if body.get("type") != "redirect":
            raise RuntimeError("Unexpected portal login response")

        self._authenticated = True

    def search_meters(
        self,
        query: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            "/portal/meters/search",
            params={
                "q": query,
                "page": page,
            },
        )

        return response.json()

    def get_energy(self, meter_id: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/portal/meters/{meter_id}/energy",
        )

        return response.json()

    def get_geo(self, meter_id: str) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/portal/meters/{meter_id}/geo",
        )

        return response.json()

    def close(self) -> None:
        self.client.close()

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        self._ensure_authenticated()

        response = self.client.request(
            method,
            url,
            **kwargs,
        )

        # Portal sessions expire. Re-authenticate once if necessary.
        if response.status_code == 401:
            self._authenticated = False
            self.login()

            response = self.client.request(
                method,
                url,
                **kwargs,
            )

        response.raise_for_status()

        return response

    def _ensure_authenticated(self) -> None:
        if not self._authenticated:
            self.login()