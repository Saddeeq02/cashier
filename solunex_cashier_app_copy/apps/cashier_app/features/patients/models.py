# -*- coding: utf-8 -*-
#apps/cashie_app/features/patients/models.py
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PatientLite:
    id: int
    patient_no: str
    full_name: str
    phone: str
    sex: str
    age: int
    created_at: str
