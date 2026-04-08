# -*- coding: utf-8 -*-
# apps/cashier_app/features/payments/api.py

from __future__ import annotations

from typing import Any, Dict, List

from shared.api.client import client


def _unwrap_list(data: Any) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("value", []) or data.get("items", []) or []
    return []


def list_pending_test_requests(patient_id: int) -> List[Dict[str, Any]]:
    data = client.get(
        "/api/test-requests",
        params={"patient_id": int(patient_id), "status": "pending"},
    )
    return _unwrap_list(data)


def list_patient_payments(patient_id: int) -> List[Dict[str, Any]]:
    data = client.get(
        "/api/payments",
        params={"patient_id": int(patient_id)},
    )
    return _unwrap_list(data)


def create_payment(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = client.post("/api/payments", json=payload)
    return data if isinstance(data, dict) else {}