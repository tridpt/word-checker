"""Hoc quy chuan dinh dang tu mot file .docx mau.

Dua mot file da dung dinh dang chuan (vi du mau cua truong/cong ty), module nay
phan tich phan than bai va suy ra mot profile: font, co chu, gian dong, canh le,
le trang, thut le dong dau... De sau do kiem cac file khac theo dung mau do.
"""

from collections import Counter

from .document import load_document

# Nguong: mot gia tri duoc coi la "hop le" neu xuat hien o it nhat ti le nay
# trong cac doan than bai.
_THRESHOLD = 0.2


def _common_values(counter: Counter, total: int, threshold: float = _THRESHOLD):
    """Tra ve cac gia tri xuat hien >= threshold; luon gom gia tri pho bien nhat."""
    if total == 0 or not counter:
        return []
    most = counter.most_common()
    result = [v for v, c in most if c / total >= threshold]
    if not result:
        result = [most[0][0]]
    return result


def _dominant(counter: Counter):
    """Tra ve gia tri pho bien nhat, hoac None neu rong."""
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def learn_profile(path: str) -> dict:
    doc = load_document(path)
    body = [p for p in doc.paragraphs if p.text.strip() and not p.is_heading]
    total = len(body)

    font_counter: Counter = Counter()
    size_counter: Counter = Counter()
    align_counter: Counter = Counter()
    spacing_counter: Counter = Counter()
    indent_counter: Counter = Counter()
    sb_counter: Counter = Counter()
    sa_counter: Counter = Counter()

    for p in body:
        for f in p.fonts:
            font_counter[f] += 1
        for s in p.sizes:
            size_counter[s] += 1
        if p.alignment is not None:
            align_counter[p.alignment] += 1
        if p.line_spacing is not None:
            spacing_counter[round(p.line_spacing, 2)] += 1
        if p.first_line_indent_cm is not None:
            indent_counter[round(p.first_line_indent_cm, 2)] += 1
        if p.space_before_pt is not None:
            sb_counter[round(p.space_before_pt, 1)] += 1
        if p.space_after_pt is not None:
            sa_counter[round(p.space_after_pt, 1)] += 1

    fonts = _common_values(font_counter, total) or ["Times New Roman"]
    sizes_raw = _common_values(size_counter, total)
    # lam tron co chu ve so nguyen neu gan (vd 13.0 -> 13)
    sizes = sorted({int(round(s)) for s in sizes_raw}) or [13, 14]

    profile = {
        "body_font_names": fonts,
        "body_font_sizes": sizes,
        "line_spacing": _dominant(spacing_counter),
        "line_spacing_tolerance": 0.05,
        "body_alignment": _dominant(align_counter),
        "margins_cm": doc.margins_cm or None,
        "margin_tolerance_cm": 0.2,
        "first_line_indent_cm": _dominant(indent_counter),
        "first_line_indent_tolerance_cm": 0.2,
        "space_before_pt": _dominant(sb_counter),
        "space_after_pt": _dominant(sa_counter),
        "paragraph_spacing_tolerance_pt": 1.0,
    }
    return profile


def describe_profile(profile: dict) -> str:
    """Tao mo ta ngan gon de in cho nguoi dung xem profile da hoc."""
    lines = [
        f"  Font:        {', '.join(profile['body_font_names'])}",
        f"  Co chu:      {', '.join(str(s) for s in profile['body_font_sizes'])} pt",
        f"  Gian dong:   {profile['line_spacing'] if profile['line_spacing'] is not None else 'khong xac dinh'}",
        f"  Canh le:     {profile['body_alignment'] or 'khong xac dinh'}",
    ]
    if profile.get("margins_cm"):
        m = profile["margins_cm"]
        lines.append(f"  Le trang:    tren {m['top']} / duoi {m['bottom']} / trai {m['left']} / phai {m['right']} cm")
    if profile.get("first_line_indent_cm") is not None:
        lines.append(f"  Thut dong dau: {profile['first_line_indent_cm']} cm")
    return "\n".join(lines)
