# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportRow:
    report_id: str
    period: str          # daily | weekly | monthly
    date_from: str
    date_to: str
    total_tests: int
    total_revenue: float
    pending_payments: float
    created_at: str
