# -*- coding: utf-8 -*-
# Cashier App
# shared/api/client.py

import requests
from typing import Any, Dict, Optional

from apps.cashier_app.app_state import state


class APIError(Exception):
    def __init__(self, status_code: int, message: str, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class APIClient:

    # ----------------------------------
    # Core request handler
    # ----------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        silent: bool = False,   # UI can suppress errors if needed
    ):

        url = f"{state.api_base_url}{path}"

        # ------------------------------
        # Build headers
        # ------------------------------
        final_headers = headers.copy() if headers else {}

        if state.access_token:
            final_headers["Authorization"] = f"Bearer {state.access_token}"

        final_headers.setdefault("Content-Type", "application/json")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=final_headers,
                json=json,
                params=params,
                timeout=state.api_timeout,
                allow_redirects=False,  # <--- ADD THIS
            )

        except requests.exceptions.RequestException as e:
            raise APIError(0, f"Network error: {str(e)}")

        # ------------------------------
        # Unauthorized (Session Expired)
        # ------------------------------
        if response.status_code == 401:
            state.clear_session()
            raise APIError(401, "Session expired. Please login again.")

        # ------------------------------
        # Handle non-success responses
        # ------------------------------
        if not response.ok:
            try:
                payload = response.json()
                message = payload.get("detail") or str(payload)
            except Exception:
                payload = None
                message = response.text

            raise APIError(response.status_code, message, payload)

        # ------------------------------
        # Parse response
        # ------------------------------
        if response.content:
            try:
                return response.json()
            except Exception:
                return response.content

        return None

    # ----------------------------------
    # Public Methods
    # ----------------------------------
    def get(self, path: str, *, params=None, **kwargs):
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, *, json=None, **kwargs):
        return self._request("POST", path, json=json, **kwargs)

    def patch(self, path: str, *, json=None, **kwargs):
        return self._request("PATCH", path, json=json, **kwargs)


client = APIClient()