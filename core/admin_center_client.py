import json
import urllib.error
import urllib.request
from typing import Any

class AdminCenterError(Exception):
    pass

class AdminCenterClient:
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key or ""

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method: str, path: str, payload: Any = None) -> Any:
        if not self.base_url:
            raise AdminCenterError("Admin Center base URL is empty.")
        url = f"{self.base_url}{path}"
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method=method, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as e:
            raise AdminCenterError(f"HTTP {e.code}: {e.reason}") from e
        except urllib.error.URLError as e:
            raise AdminCenterError(f"Connection error: {e.reason}") from e
        except Exception as e:
            raise AdminCenterError(str(e)) from e

    def health(self) -> Any:
        return self._request("GET", "/api/health")

    def get_employees(self) -> list[dict]:
        data = self._request("GET", "/api/employees")
        if isinstance(data, dict) and "employees" in data:
            return data["employees"] or []
        if isinstance(data, list):
            return data
        return []

    def push_staffroot_summary(self, payload: dict) -> Any:
        return self._request("POST", "/api/integrations/staffroot/sync", payload)
