# -*- coding: utf-8 -*-
# apps/cashier_app/features/test_requests/api.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from shared.api.client import client


@dataclass(frozen=True)
class CreateTestRequestPayload:
    patient_id: int
    test_type_id: int
    requested_by: Optional[str] = None
    requested_note: Optional[str] = None


def _unwrap_list(payload: Any) -> list[dict]:
    """
    Backend sometimes returns a list, sometimes { "value": [...] }.
    Normalize to list[dict].
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        v = payload.get("value")
        if isinstance(v, list):
            return v
    return []


def list_test_types() -> list[dict]:
    payload = client.get("/api/test-types")
    return _unwrap_list(payload)


def create_test_request(payload: CreateTestRequestPayload) -> dict:
    return client.post(
        "/api/test-requests",
        json={
            "patient_id": int(payload.patient_id),
            "test_type_id": int(payload.test_type_id),
            "requested_by": payload.requested_by,
            "requested_note": payload.requested_note,
        },
    )


def list_test_requests(
    *,
    patient_id: int,
    status: Optional[str] = None,
    limit: int = 200,
) -> list[dict]:
    params = {"patient_id": int(patient_id), "limit": int(limit)}
    if status:
        params["status"] = str(status)

    payload = client.get("/api/test-requests", params=params)
    return _unwrap_list(payload)