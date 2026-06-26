"""Xuat bao cao ket qua kiem tra ra file PDF (ho tro tieng Viet)."""

import os

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from .issues import SEVERITY_ERROR, Issue
from .report import summarize, _sort_key, aggregate_issues

_BLUE = (43, 108, 176)
_GREY = (90, 100, 110)


def _find_fonts():
    """Tim cap font (regular, bold) co glyph tieng Viet."""
    candidates = [
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\times.ttf", r"C:\Windows\Fonts\timesbd.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg) and os.path.exists(bold):
            return reg, bold
    for reg, bold in candidates:
        if os.path.exists(reg):
            return reg, reg
    return None, None


def write_pdf(out_path: str, src_path: str, issues: list[Issue], stats: dict | None = None) -> None:
    reg, bold = _find_fonts()
    if not reg:
        raise RuntimeError(
            "Khong tim thay font Unicode (arial.ttf / DejaVuSans.ttf) de tao PDF."
        )

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("vn", "", reg)
    pdf.add_font("vn", "B", bold)

    # Tieu de
    pdf.set_font("vn", "B", 16)
    pdf.set_text_color(*_BLUE)
    pdf.cell(0, 10, "Bao cao kiem tra chinh ta & dinh dang",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("vn", "", 10)
    pdf.set_text_color(*_GREY)
    pdf.cell(0, 6, f"File: {os.path.basename(src_path)}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if stats:
        pdf.cell(0, 6,
                 f"Thong ke: {stats['words']} tu, {stats['paragraphs']} doan, "
                 f"{stats['headings']} tieu de, ~{stats['estimated_pages']} trang, "
                 f"~{stats['reading_minutes']} phut doc",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    s = summarize(issues)
    pdf.ln(2)
    pdf.set_text_color(20, 20, 20)
    pdf.set_font("vn", "B", 11)
    pdf.cell(0, 7, f"Tong cong: {s['total']} van de (loi nghiem trong: {s['errors']})",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    if not issues:
        pdf.set_font("vn", "B", 12)
        pdf.set_text_color(*(47, 133, 90))
        pdf.cell(0, 8, "Khong phat hien loi nao. File san sang de nop!",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.output(out_path)
        return

    # Bang loi
    pdf.set_font("vn", "", 9)
    pdf.set_text_color(20, 20, 20)
    with pdf.table(
        col_widths=(18, 20, 62, 50),
        text_align=("LEFT", "LEFT", "LEFT", "LEFT"),
        line_height=5,
        first_row_as_headings=True,
    ) as table:
        header = table.row()
        for h in ("Muc do", "Vi tri", "Mo ta", "Goi y"):
            header.cell(h)
        for it in sorted(aggregate_issues(issues), key=_sort_key):
            row = table.row()
            row.cell("Loi" if it.severity == SEVERITY_ERROR else "Canh bao")
            row.cell(it.location())
            row.cell(f"[{it.category}] {it.message}")
            row.cell(it.suggestion or "")

    pdf.output(out_path)
