import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class IdentityProviderError(Exception):
    pass


class IdentityProviderClient:
    """Optional directory connector. StaffRoot local accounts remain authoritative by default."""

    def __init__(self, base_url: str, api_token: str = ""):
        self.base_url = (base_url or "").rstrip("/")
        self.api_token = api_token or ""
        parsed = urllib.parse.urlparse(self.base_url)
        if self.base_url and parsed.scheme not in {"http", "https"}:
            raise IdentityProviderError("Identity provider URL must use HTTP or HTTPS.")

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _request(self, method: str, path: str, payload: Any = None) -> Any:
        if not self.base_url:
            raise IdentityProviderError("Organization identity URL is empty.")
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=data, method=method, headers=self._headers()
        )
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                body = response.read(2 * 1024 * 1024 + 1)
                if len(body) > 2 * 1024 * 1024:
                    raise IdentityProviderError("Identity provider response exceeded size limit.")
                return json.loads(body.decode("utf-8")) if body else None
        except urllib.error.HTTPError as exc:
            raise IdentityProviderError(f"HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise IdentityProviderError(f"Connection error: {exc.reason}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IdentityProviderError("Identity provider returned invalid JSON.") from exc

    def health(self) -> Any:
        return self._request("GET", "/api/health")

    def get_employees(self) -> list[dict]:
        data = self._request("GET", "/api/employees")
        if isinstance(data, dict):
            data = data.get("employees", [])
        return data if isinstance(data, list) else []
