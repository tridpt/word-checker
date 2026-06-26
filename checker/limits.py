"""Kiem tra gioi han so tu / so trang (vd: bai phai duoi 2000 tu)."""

from .document import DocInfo
from .issues import CATEGORY_LIMIT, SEVERITY_ERROR, Issue
from .stats import compute_stats


def check_limits(doc: DocInfo, limits: dict | None) -> list[Issue]:
    """limits: {'min_words','max_words','max_pages'} — gia tri None thi bo qua."""
    if not limits:
        return []
    stats = compute_stats(doc)
    issues = []

    min_w = limits.get("min_words")
    max_w = limits.get("max_words")
    max_p = limits.get("max_pages")

    if max_w is not None and stats["words"] > max_w:
        issues.append(Issue(
            category=CATEGORY_LIMIT, severity=SEVERITY_ERROR,
            message=f"Vuot gioi han so tu: {stats['words']} tu (toi da {max_w})",
            suggestion=f"Cat bot khoang {stats['words'] - max_w} tu",
        ))
    if min_w is not None and stats["words"] < min_w:
        issues.append(Issue(
            category=CATEGORY_LIMIT, severity=SEVERITY_ERROR,
            message=f"Thieu so tu: {stats['words']} tu (toi thieu {min_w})",
            suggestion=f"Viet them khoang {min_w - stats['words']} tu",
        ))
    if max_p is not None and stats["estimated_pages"] > max_p:
        issues.append(Issue(
            category=CATEGORY_LIMIT, severity=SEVERITY_ERROR,
            message=f"Vuot gioi han so trang (uoc tinh): {stats['estimated_pages']} trang (toi da {max_p})",
            suggestion="Rut gon noi dung",
        ))
    return issues
