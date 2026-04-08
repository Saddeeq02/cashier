# -*- coding: utf-8 -*-
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import mm

import sys
import os
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Windows Printing Imports
try:
    import win32print
    import win32api
except ImportError:
    win32print = None

def _get_base_path():
    """
    Works for both:
    - Development (normal Python)
    - Packaged EXE (PyInstaller)
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]

BASE_DIR = _get_base_path()
FONT_DIR = BASE_DIR / "assets" / "fonts"

# =========================
# FONT REGISTRATION
# =========================
try:
    pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
    FONT = "DejaVu"
    FONT_BOLD = "DejaVu-Bold"
    print("✅ DejaVu font loaded from:", FONT_DIR)
except Exception as e:
    print("⚠️ Font load failed:", e)
    FONT = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"


class CashierReceiptService:

    @staticmethod
    def generate(receipt_data, output_path, paper_width="80mm"):
        """
        Generates an Enterprise-Grade PDF receipt optimized for thermal printers.
        """
        # =========================
        # PAPER CONFIG
        # =========================
        width = 58 * mm if paper_width == "58mm" else 80 * mm

        # Extra-long canvas allows the thermal printer to cut exactly where content ends
        doc = SimpleDocTemplate(
            output_path,
            pagesize=(width, 300 * mm),
            leftMargin=3 * mm,   # Slightly increased for a cleaner visual border
            rightMargin=3 * mm,
            topMargin=4 * mm,
            bottomMargin=4 * mm
        )

        styles = getSampleStyleSheet()

        # =========================
        # STYLES (ENTERPRISE POLISH)
        # =========================
        title_style = ParagraphStyle(
            name="title",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=12,        # Increased for clear brand visibility
            leading=14,         # Generous breathing room
            fontName=FONT_BOLD
        )

        subtitle_style = ParagraphStyle(
            name="subtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=9,         # Highly visible, not bold
            leading=12,
            fontName=FONT
        )

        body_style = ParagraphStyle(
            name="body",
            parent=styles["Normal"],
            alignment=TA_LEFT,
            fontSize=10,        # Large enough to read at a glance
            leading=13,         # Clean vertical spacing
            fontName=FONT
        )

        center_small = ParagraphStyle(
            name="center_small",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=8.5,       # Legible footer size
            leading=11,
            fontName=FONT
        )

        elements = []

        # =========================
        # HEADER
        # =========================
        elements.append(Paragraph("I AND E DIAGNOSTIC LABORATORY", title_style))
        elements.append(Paragraph("& ULTRASOUND LTD", title_style))
        elements.append(Spacer(1, 3 * mm))
        
        elements.append(Paragraph("No 514 Zaria Road, Kano", subtitle_style))
        elements.append(Paragraph("Opp. First Bank, Yar Akwa", subtitle_style))
        elements.append(Paragraph("Tel: 08063645308", subtitle_style))
        
        # Horizontal Divider (Crisp and subtle)
        elements.append(Spacer(1, 3 * mm))
        elements.append(Table([[""]], colWidths=[width - 6*mm], 
                       style=[('LINEBELOW', (0,0), (-1,-1), 0.5, colors.darkgrey)]))
        elements.append(Spacer(1, 3 * mm))

        # =========================
        # PATIENT & CASHIER INFO
        # =========================
        # Using simple string formatting without aggressive bolding
        elements.append(Paragraph(f"<b>Patient ID:</b> &nbsp;{receipt_data['patient_no']}", body_style))
        elements.append(Paragraph(f"<b>Name:</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{receipt_data['patient_name']}", body_style))
        elements.append(Paragraph(f"<b>Date:</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{receipt_data['created_at']}", body_style))
        elements.append(Paragraph(f"<b>Cashier:</b> &nbsp;&nbsp;&nbsp;&nbsp;{receipt_data['created_by']}", body_style))
        
        elements.append(Spacer(1, 4 * mm))

        # =========================
        # ITEMS TABLE
        # =========================
        table_data = [["Desc", "Test", "Amount"]]
        total_val = 0
        currency_symbol = "₦"

        for t in receipt_data["tests"]:
            name = t["name"]
            price = float(t["price"])
            total_val += price
            table_data.append([name, f"{currency_symbol}{price:,.2f}"])

        # Table dimensions adjusted safely inside margins
        item_table = Table(table_data, colWidths=[width * 0.58, width * 0.34])
        item_table.setStyle(TableStyle([
            # Header Row
            ("FONT", (0, 0), (-1, 0), FONT_BOLD, 10),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
            
            # Data Rows
            ("FONT", (0, 1), (-1, -1), FONT, 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(item_table)

        # =========================
        # TOTAL SECTION
        # =========================
        elements.append(Spacer(1, 2 * mm))
        total_table = Table([["TOTAL", f"{currency_symbol}{total_val:,.2f}"]], 
                            colWidths=[width * 0.58, width * 0.34])
        total_table.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), FONT_BOLD, 12), # High emphasis on total
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LINEABOVE", (0, 0), (-1, -1), 1, colors.black),
            ("LINEBELOW", (0, 0), (-1, -1), 2, colors.black), # Double thickness under total
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(total_table)

        # =========================
        # FOOTER
        # =========================
        elements.append(Spacer(1, 6 * mm))
        elements.append(Paragraph("Thank you for choosing us.", center_small))
        elements.append(Paragraph("Please present this receipt at the lab.", center_small))
        elements.append(Spacer(1, 3 * mm))
        
        elements.append(Paragraph("<b>Portal:</b> www.iandelaboratory.com", center_small))
        elements.append(Paragraph("<b>Login:</b> Phone (User) | Patient ID (Pass)", center_small))
        
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph("Powered by Solunex Technologies", center_small))

        # Build PDF
        doc.build(elements)
        return output_path

    @staticmethod
    def print_to_windows_printer(pdf_path, printer_name=None):
        """
        Sends the generated PDF directly to a Windows Printer.
        Requires: pip install pywin32
        """
        if not win32print:
            print("❌ pywin32 is not installed. Skipping print.")
            return False

        if printer_name is None:
            printer_name = win32print.GetDefaultPrinter()

        try:
            print(f"🖨️ Printing to: {printer_name}")
            win32api.ShellExecute(0, "print", str(pdf_path), None, ".", 0)
            return True
        except Exception as e:
            print(f"❌ Windows Print Error: {e}")
            return False