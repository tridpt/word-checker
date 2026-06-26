"""Kiem tra dinh dang cua tai lieu theo profile trong config."""

from collections import Counter

from .document import DocInfo, ParagraphInfo
from .issues import CATEGORY_FORMAT, SEVERITY_ERROR, SEVERITY_WARNING, Issue
from .mathdetect import is_math_heavy


def _excerpt(text: str, n: int = 60) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


def _check_font(p: ParagraphInfo, allowed: list[str]) -> list[Issue]:
    issues = []
    bad = {f for f in p.fonts if f not in allowed}
    if bad:
        issues.append(
            Issue(
                category=CATEGORY_FORMAT,
                severity=SEVERITY_ERROR,
                message=f"Font khong dung: dung '{', '.join(sorted(bad))}', yeu cau '{', '.join(allowed)}'",
                paragraph=p.number,
                excerpt=_excerpt(p.text),
                suggestion=f"Doi font ve {allowed[0]}",
            )
        )
    return issues


def _check_size(p: ParagraphInfo, allowed: list[int]) -> list[Issue]:
    issues = []
    allowed_set = set(float(s) for s in allowed)
    bad = {s for s in p.sizes if s not in allowed_set}
    if bad:
        bad_str = ", ".join(f"{b:g}" for b in sorted(bad))
        allowed_str = ", ".join(str(s) for s in allowed)
        issues.append(
            Issue(
                category=CATEGORY_FORMAT,
                severity=SEVERITY_ERROR,
                message=f"Co chu khong dung: dung {bad_str}pt, yeu cau {allowed_str}pt",
                paragraph=p.number,
                excerpt=_excerpt(p.text),
                suggestion=f"Doi co chu ve {allowed[0]}pt",
            )
        )
    return issues


def _check_alignment(p: ParagraphInfo, required: str | None) -> list[Issue]:
    if required is None or p.alignment is None:
        return []
    # Bo qua doan ngan (tieu de, chu thich hinh/bang, trang bia, dong ky ten...):
    # cac doan nay thuong canh giua/phai mot cach co chu y, khong phai loi.
    if len(p.text.split()) < 12:
        return []
    if p.alignment != required:
        name_map = {"justify": "canh deu", "left": "canh trai", "center": "canh giua", "right": "canh phai"}
        return [
            Issue(
                category=CATEGORY_FORMAT,
                severity=SEVERITY_WARNING,
                message=f"Canh le la '{name_map.get(p.alignment, p.alignment)}', yeu cau '{name_map.get(required, required)}'",
                paragraph=p.number,
                excerpt=_excerpt(p.text),
                suggestion=f"Doi sang {name_map.get(required, required)}",
            )
        ]
    return []


def _check_line_spacing(p: ParagraphInfo, required: float | None, tol: float) -> list[Issue]:
    if required is None or p.line_spacing is None:
        return []
    if abs(p.line_spacing - required) > tol:
        return [
            Issue(
                category=CATEGORY_FORMAT,
                severity=SEVERITY_WARNING,
                message=f"Gian dong la {p.line_spacing:g}, yeu cau {required:g}",
                paragraph=p.number,
                excerpt=_excerpt(p.text),
                suggestion=f"Dat gian dong = {required:g}",
            )
        ]
    return []


def _check_indent_spacing(p: ParagraphInfo, profile: dict) -> list[Issue]:
    issues = []
    fli_req = profile.get("first_line_indent_cm")
    if fli_req is not None and p.first_line_indent_cm is not None:
        tol = profile.get("first_line_indent_tolerance_cm", 0.2)
        if abs(p.first_line_indent_cm - fli_req) > tol:
            issues.append(
                Issue(
                    category=CATEGORY_FORMAT,
                    severity=SEVERITY_WARNING,
                    message=f"Thut le dong dau = {p.first_line_indent_cm:g}cm, yeu cau {fli_req:g}cm",
                    paragraph=p.number,
                    excerpt=_excerpt(p.text),
                    suggestion=f"Dat thut le dong dau = {fli_req:g}cm",
                )
            )

    tol_pt = profile.get("paragraph_spacing_tolerance_pt", 1.0)
    sb_req = profile.get("space_before_pt")
    if sb_req is not None and p.space_before_pt is not None:
        if abs(p.space_before_pt - sb_req) > tol_pt:
            issues.append(
                Issue(
                    category=CATEGORY_FORMAT,
                    severity=SEVERITY_WARNING,
                    message=f"Khoang cach truoc doan = {p.space_before_pt:g}pt, yeu cau {sb_req:g}pt",
                    paragraph=p.number,
                    excerpt=_excerpt(p.text),
                    suggestion=f"Dat khoang cach truoc doan = {sb_req:g}pt",
                )
            )
    sa_req = profile.get("space_after_pt")
    if sa_req is not None and p.space_after_pt is not None:
        if abs(p.space_after_pt - sa_req) > tol_pt:
            issues.append(
                Issue(
                    category=CATEGORY_FORMAT,
                    severity=SEVERITY_WARNING,
                    message=f"Khoang cach sau doan = {p.space_after_pt:g}pt, yeu cau {sa_req:g}pt",
                    paragraph=p.number,
                    excerpt=_excerpt(p.text),
                    suggestion=f"Dat khoang cach sau doan = {sa_req:g}pt",
                )
            )
    return issues


def check_formatting(doc: DocInfo, profile: dict, skip_math: bool = True) -> list[Issue]:
    issues: list[Issue] = []

    body = [p for p in doc.paragraphs if p.text.strip() and not p.is_heading]
    # Tach rieng cac doan cong thuc de bo qua kiem tra font/co chu/gian dong
    # (cong thuc thuong dung font va co chu rieng -> de bao nham).
    prose = [p for p in body if not (skip_math and is_math_heavy(p.text))]

    for p in prose:
        issues += _check_font(p, profile["body_font_names"])
        issues += _check_size(p, profile["body_font_sizes"])
        issues += _check_alignment(p, profile.get("body_alignment"))
        issues += _check_line_spacing(
            p, profile.get("line_spacing"), profile.get("line_spacing_tolerance", 0.05)
        )
        issues += _check_indent_spacing(p, profile)

    # Kiem tra dong nhat: chi xet tren cac doan van xuoi (bo cong thuc)
    issues += _check_consistency(prose)

    # Kiem tra le trang
    issues += _check_margins(doc, profile)

    return issues


def _check_consistency(body: list[ParagraphInfo]) -> list[Issue]:
    issues = []
    font_counter = Counter()
    size_counter = Counter()
    for p in body:
        for f in p.fonts:
            font_counter[f] += 1
        for s in p.sizes:
            size_counter[s] += 1

    if len(font_counter) > 1:
        common = font_counter.most_common()
        issues.append(
            Issue(
                category=CATEGORY_FORMAT,
                severity=SEVERITY_WARNING,
                message="Body dung nhieu font khac nhau: "
                + ", ".join(f"{name} ({cnt} doan)" for name, cnt in common),
                paragraph=None,
                suggestion="Thong nhat ve mot font duy nhat",
            )
        )
    if len(size_counter) > 1:
        common = size_counter.most_common()
        issues.append(
            Issue(
                category=CATEGORY_FORMAT,
                severity=SEVERITY_WARNING,
                message="Body dung nhieu co chu khac nhau: "
                + ", ".join(f"{size:g}pt ({cnt} doan)" for size, cnt in common),
                paragraph=None,
                suggestion="Thong nhat ve mot co chu cho than bai",
            )
        )
    return issues


def _check_margins(doc: DocInfo, profile: dict) -> list[Issue]:
    issues = []
    required = profile.get("margins_cm")
    if not required or not doc.margins_cm:
        return []
    tol = profile.get("margin_tolerance_cm", 0.2)
    label = {"top": "tren", "bottom": "duoi", "left": "trai", "right": "phai"}
    for side, req in required.items():
        if req is None:
            continue
        actual = doc.margins_cm.get(side)
        if actual is None:
            continue
        if abs(actual - req) > tol:
            issues.append(
                Issue(
                    category=CATEGORY_FORMAT,
                    severity=SEVERITY_WARNING,
                    message=f"Le {label.get(side, side)} = {actual:g}cm, yeu cau {req:g}cm",
                    paragraph=None,
                    suggestion=f"Dat le {label.get(side, side)} = {req:g}cm",
                )
            )
    return issues
