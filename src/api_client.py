from typing import Any, Dict, Optional
import requests
from requests.exceptions import HTTPError, RequestException, Timeout
import json

class APIClient:
    """Универсальная обёртка над библиотекой requests."""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Внутренний метод для отправки HTTP-запросов."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Объединяем дефолтные заголовки сессии с переданными в метод
        request_headers = {**self.session.headers, **(headers or {})}

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
            )

            # Вызывает HTTPError, если статус-код 4xx или 5xx
            response.raise_for_status()

            # Пытаемся вернуть JSON, если он есть в ответе
            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()

            return {"text": response.text, "status_code": response.status_code}

        except Timeout:
            raise TimeoutError(f"Превышено время ожидания ({self.timeout}с) для {url}")
        except HTTPError as http_err:
            raise HTTPError(
                f"HTTP ошибка при запросе к {url}: {http_err} (Код: {http_err.status_code})"
            )
        except RequestException as req_err:
            raise RequestException(f"Ошибка сети при запросе к {url}: {req_err}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[dict] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """GET-запрос"""
        return self._send_request("GET", endpoint, params=params, headers= headers, **kwargs)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """POST-запрос"""
        return self._send_request("POST", endpoint, json=json, **kwargs)