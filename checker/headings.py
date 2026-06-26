"""Kiem tra tieu de muc va danh so de muc.

Hai loai kiem tra:
1. Nhay cap tieu de (level jump): vi du Heading 1 roi nhay thang sang Heading 3
   ma khong co Heading 2 o giua.
2. Danh so de muc khong lien tuc: vi du "1.", "2.", "4." (thieu "3."), hoac muc
   con bat dau tu 2 thay vi 1. Chi ap dung cho tieu de CO danh so bang chu trong
   noi dung (khong ap dung neu dung danh so tu dong cua Word).
"""

import re

from .document import DocInfo, ParagraphInfo
from .issues import CATEGORY_HEADING, SEVERITY_WARNING, Issue

# Khop so de muc o dau tieu de: "1", "1.", "1.2", "2.3.1." ...
_NUM_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+\S")


def _heading_level(p: ParagraphInfo) -> int | None:
    """Tra ve cap tieu de (1, 2, 3...) tu ten style, hoac None neu khong phai."""
    m = re.match(r"Heading (\d+)", p.style_name)
    if m:
        return int(m.group(1))
    return None


def _excerpt(text: str, n: int = 60) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


def _check_level_jumps(headings: list[ParagraphInfo]) -> list[Issue]:
    issues = []
    prev_level = 0
    for p in headings:
        level = _heading_level(p)
        if level is None:
            continue
        if level > prev_level + 1:
            expected = prev_level + 1
            issues.append(
                Issue(
                    category=CATEGORY_HEADING,
                    severity=SEVERITY_WARNING,
                    message=f"Nhay cap tieu de: dung Heading {level} sau cap {prev_level} "
                            f"(thieu Heading {expected})",
                    paragraph=p.number,
                    excerpt=_excerpt(p.text),
                    suggestion=f"Dung Heading {expected} hoac bo sung cap trung gian",
                )
            )
        prev_level = level
    return issues


def _parse_number(text: str):
    m = _NUM_RE.match(text)
    if not m:
        return None
    return tuple(int(x) for x in m.group(1).split("."))


def _check_numbering_sequence(headings: list[ParagraphInfo]) -> list[Issue]:
    issues = []
    last_child: dict[tuple, int] = {}
    for p in headings:
        num = _parse_number(p.text)
        if num is None:
            continue
        parent, child = num[:-1], num[-1]
        expected = last_child.get(parent, 0) + 1
        if child != expected:
            num_str = ".".join(str(x) for x in num)
            expected_str = ".".join(str(x) for x in (parent + (expected,)))
            issues.append(
                Issue(
                    category=CATEGORY_HEADING,
                    severity=SEVERITY_WARNING,
                    message=f"Danh so de muc khong lien tuc: '{num_str}' (mong doi '{expected_str}')",
                    paragraph=p.number,
                    excerpt=_excerpt(p.text),
                    suggestion=f"Kiem tra lai thu tu danh so muc",
                )
            )
        # Cap nhat theo so thuc te de tranh bao loi day chuyen
        last_child[parent] = child
    return issues


def check_headings(doc: DocInfo, checks: dict | None = None) -> list[Issue]:
    checks = checks or {"level_jump": True, "numbering_sequence": True}
    headings = [p for p in doc.paragraphs if p.text.strip() and p.is_heading]
    issues: list[Issue] = []
    if checks.get("level_jump", True):
        issues += _check_level_jumps(headings)
    if checks.get("numbering_sequence", True):
        issues += _check_numbering_sequence(headings)
    return issues
