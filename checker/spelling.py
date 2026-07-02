"""Kiem tra chinh ta tieng Viet dua tren tu dien loi thuong gap (offline).

Day la cach tiep can deterministic, an toan (it bao nham): chi bao loi voi cac
cum tu/co nam trong danh sach common_typos.txt. De mo rong do chinh xac, ban co
the bo sung them cap loi vao file tu dien do.
"""

import os
import re

from .document import DocInfo, ParagraphInfo
from .issues import CATEGORY_SPELLING, SEVERITY_ERROR, Issue
from .resources import resource_path

_DICT_PATH = resource_path("dictionaries", "common_typos.txt")


def load_typo_dict(path: str = _DICT_PATH) -> dict[str, str]:
    typos: dict[str, str] = {}
    if not os.path.exists(path):
        return typos
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            wrong, _, right = line.partition("=")
            wrong, right = wrong.strip(), right.strip()
            if wrong and right:
                typos[wrong.lower()] = right
    return typos


def _build_pattern(typos: dict[str, str]) -> re.Pattern | None:
    if not typos:
        return None
    # sap xep dai truoc de uu tien khop cum tu nhieu chu
    keys = sorted(typos.keys(), key=len, reverse=True)
    # bao quanh boi ranh gioi (khong phai chu cai) de tranh khop giua tu
    alts = "|".join(re.escape(k) for k in keys)
    return re.compile(r"(?<!\w)(" + alts + r")(?!\w)", re.IGNORECASE | re.UNICODE)


def _excerpt_around(text: str, pos: int, width: int = 25) -> str:
    start = max(0, pos - width)
    end = min(len(text), pos + width)
    snippet = text[start:end].replace("\n", " ")
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


def check_spelling(doc: DocInfo, typos: dict[str, str] | None = None) -> list[Issue]:
    if typos is None:
        typos = load_typo_dict()
    pattern = _build_pattern(typos)
    if pattern is None:
        return []

    issues: list[Issue] = []
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        for m in pattern.finditer(p.text):
            found = m.group(1)
            correct = typos.get(found.lower(), "")
            issues.append(
                Issue(
                    category=CATEGORY_SPELLING,
                    severity=SEVERITY_ERROR,
                    message=f"Co the sai chinh ta: '{found}'",
                    paragraph=p.number,
                    excerpt=_excerpt_around(p.text, m.start()),
                    suggestion=f"Co the la '{correct}'",
                )
            )

    # Kiem chinh ta trong bang, dau/chan trang, text box (loi cap tai lieu)
    for seg in getattr(doc, "extra_segments", None) or []:
        if not seg.text.strip():
            continue
        for m in pattern.finditer(seg.text):
            found = m.group(1)
            correct = typos.get(found.lower(), "")
            issues.append(
                Issue(
                    category=CATEGORY_SPELLING,
                    severity=SEVERITY_ERROR,
                    message=f"[{seg.location}] Co the sai chinh ta: '{found}'",
                    paragraph=None,
                    excerpt=_excerpt_around(seg.text, m.start()),
                    suggestion=f"Co the la '{correct}'",
                )
            )
    return issues
