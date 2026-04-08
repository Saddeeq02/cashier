# -*- coding: utf-8 -*-
# shared/uix/theme.py

from __future__ import annotations
from PySide6.QtWidgets import QApplication

# ==========================================================
# ENTERPRISE LABORATORY PALETTE (Clinical Grade)
# ==========================================================
SOLUNEX = {
    # Base "Sterile" background - slightly cool-toned to look cleaner than pure white
    "bg": "#F1F5F9", 
    "panel": "#FFFFFF",
    "panel_soft": "#F8FAFC",
    "panel_elevated": "#FFFFFF",

    # Typography - High contrast for readability of medical results
    "text": "#1E293B",      # Slate 800
    "muted": "#64748B",     # Slate 500
    "subtle": "#94A3B8",    # Slate 400

    # Laboratory Brand Colors
    # Using "Clinical Teal/Blue" - associated with cleanliness and precision
    "primary": "#0D9488",        # Teal 600 (The "Lab" color)
    "primary_hover": "#0F766E",  # Teal 700
    "primary_soft": "#F0FDFA",   # Teal 50 (Used for active row highlights)

    # Accent for actionable items
    "accent": "#0284C7",        # Sky Blue 600
    "accent_soft": "#F0F9FF",

    # Status Colors (Critical for Lab results)
    "success": "#10B981",       # Emerald 600 (Normal Results)
    "success_soft": "#ECFDF5",

    "warning": "#F59E0B",       # Amber 500 (Abnormal / High)
    "warning_soft": "#FFFBEB",

    "danger": "#E11D48",        # Rose 600 (Critical Flag)
    "danger_soft": "#FFF1F2",

    # Borders / Depth (Thinner, more precise borders)
    "border": "#CBD5E1",        # Slate 300
    "border_light": "#E2E8F0",  # Slate 200
    "border_focus": "#0D9488",  # Match Primary
}


def _qss() -> str:
    c = SOLUNEX

    return f"""
/* ==========================================================
    GLOBAL BASE
========================================================== */
* {{
    font-family: "Inter", "Segoe UI", system-ui; /* Inter is the standard for modern enterprise UI */
    font-size: 9pt; /* Smaller font for higher information density */
    color: {c["text"]};
}}

QWidget {{
    background: {c["bg"]};
}}

/* ==========================================================
    PANELS & CONTAINERS
========================================================== */
QFrame#Panel {{
    background: {c["panel"]};
    border: 1px solid {c["border_light"]};
    border-radius: 8px; /* Sharper corners feel more "Industrial/Enterprise" */
}}

QFrame#PanelAlt {{
    background: {c["panel_soft"]};
    border: 1px solid {c["border_light"]};
    border-radius: 8px;
}}

QFrame#HeaderBar {{
    background: {c["panel"]};
    border-bottom: 2px solid {c["primary"]}; /* Distinctive brand line */
}}

/* ==========================================================
    SIDEBAR (Professional Clinical Style)
========================================================== */
QWidget#Sidebar {{
    background: #1E293B; /* Dark sidebar is standard for Enterprise SaaS */
    border-right: none;
}}

QPushButton#NavItem {{
    text-align: left;
    padding: 10px 15px;
    margin: 2px 8px;
    border-radius: 6px;
    background: transparent;
    color: #94A3B8;
    font-weight: 500;
}}

QPushButton#NavItem:hover {{
    background: #334155;
    color: white;
}}

QPushButton#NavItem[active="true"] {{
    background: {c["primary"]};
    color: white;
    font-weight: 600;
}}

/* ==========================================================
    TABLE SYSTEM (The core of a Lab App)
========================================================== */
QTableWidget {{
    background: {c["panel"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    gridline-color: {c["border_light"]};
    selection-background-color: {c["primary_soft"]};
    selection-color: {c["primary"]};
    outline: none;
}}

QHeaderView::section {{
    background: {c["panel_soft"]};
    padding: 10px;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 8pt;
    color: {c["muted"]};
    border: none;
    border-bottom: 2px solid {c["border"]};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {c["border_light"]};
}}

/* ==========================================================
    INPUTS & FIELDS
========================================================== */
QLineEdit, QComboBox, QTextEdit {{
    background: #FFFFFF;
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 6px 10px;
}}

QLineEdit:focus {{
    border: 2px solid {c["primary"]};
    background: #FFFFFF;
}}

/* ==========================================================
    STATUS INDICATORS (Clinical Flags)
========================================================== */
QLabel#StatusCritical {{
    color: {c["danger"]};
    background: {c["danger_soft"]};
    border: 1px solid {c["danger"]};
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 800;
}}

QLabel#StatusNormal {{
    color: {c["success"]};
    background: {c["success_soft"]};
    border: 1px solid {c["success"]};
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
}}

/* ==========================================================
    BUTTONS
========================================================== */
QPushButton {{
    background: {c["panel"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton#Primary {{
    background: {c["primary"]};
    color: white;
    border: none;
}}

QPushButton#Primary:hover {{
    background: {c["primary_hover"]};
}}

"""

def apply_solunex_theme(app: QApplication) -> None:
    app.setStyleSheet(_qss())