from typing import Any

import requests

from desktop_client.config import API_BASE_URL


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, timeout=15, **kwargs)
        if response.status_code >= 400:
            try:
                message = response.json().get("detail", response.text)
            except ValueError:
                message = response.text
            raise ApiError(message)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, payload: dict) -> Any:
        return self._request("POST", path, json=payload)

    def put(self, path: str, payload: dict) -> Any:
        return self._request("PUT", path, json=payload)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)
