# -*- coding: utf-8 -*-
# apps/cashier_app/features/patients/api.py

from __future__ import annotations
from typing import Optional

from shared.api.client import client


def create_patient(payload: dict) -> dict:
    return client.post("/api/patients", json=payload)


def search_patients(q: Optional[str] = None, created_date: Optional[str] = None) -> list[dict]:
    """
    Search patients by keyword 'q' OR fetch the daily queue using 'created_date'.
    """
    params = {}
    if q:
        params["q"] = q
    if created_date:
        params["created_date"] = created_date
        
    return client.get("/api/patients/search", params=params)


def get_patient(patient_id: int) -> dict:
    return client.get(f"/api/patients/{patient_id}")


def update_patient(patient_id: int, payload: dict) -> dict:
    """
    Updates patient biodata. 
    Uses PATCH to update only the fields provided in the payload.
    """
    return client.patch(f"/api/patients/{patient_id}", json=payload)