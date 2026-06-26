"""Kiem tra loi co hoc trong van ban (deterministic, khong phu thuoc ngon ngu)."""

import re

from .document import DocInfo, ParagraphInfo
from .issues import CATEGORY_TEXT, SEVERITY_ERROR, SEVERITY_WARNING, Issue
from .mathdetect import is_math_heavy

# Dau cau ket thuc / phan cach
_PUNCT_AFTER = ",;:"          # bat buoc co dau cach phia sau
_PUNCT_NO_SPACE_BEFORE = ",.;:!?)"  # khong duoc co dau cach phia truoc


def _excerpt_around(text: str, pos: int, width: int = 25) -> str:
    start = max(0, pos - width)
    end = min(len(text), pos + width)
    snippet = text[start:end].replace("\n", " ")
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


def _check_double_space(p: ParagraphInfo) -> list[Issue]:
    issues = []
    for m in re.finditer(r"  +", p.text):
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message="Co nhieu dau cach lien tiep (cach doi)",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, m.start()),
                suggestion="Thay bang mot dau cach",
            )
        )
    return issues


def _check_space_before_punct(p: ParagraphInfo) -> list[Issue]:
    issues = []
    for m in re.finditer(r"\s+([" + re.escape(_PUNCT_NO_SPACE_BEFORE) + r"])", p.text):
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message=f"Co dau cach thua truoc dau '{m.group(1)}'",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, m.start()),
                suggestion="Bo dau cach truoc dau cau",
            )
        )
    return issues


def _check_missing_space_after_punct(p: ParagraphInfo) -> list[Issue]:
    issues = []
    # dau , ; : khong theo sau boi khoang trang/cuoi cau, va khong phai giua hai chu so
    for m in re.finditer(r"([,;:])(?=\S)", p.text):
        pos = m.start()
        ch = m.group(1)
        # bo qua truong hop so : so (gio) hoac so,so (so thap phan kieu chau Au)
        before = p.text[pos - 1] if pos > 0 else ""
        after = p.text[pos + 1] if pos + 1 < len(p.text) else ""
        if before.isdigit() and after.isdigit():
            continue
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message=f"Thieu dau cach sau dau '{ch}'",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, pos),
                suggestion="Them mot dau cach sau dau cau",
            )
        )
    return issues


def _check_trailing_space(p: ParagraphInfo) -> list[Issue]:
    if p.text and p.text != p.text.rstrip() and p.text.strip():
        return [
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message="Co khoang trang thua o cuoi doan",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, len(p.text.rstrip())),
                suggestion="Xoa khoang trang cuoi doan",
            )
        ]
    return []


def _check_space_in_parens(p: ParagraphInfo) -> list[Issue]:
    issues = []
    for m in re.finditer(r"\(\s+|\s+\)", p.text):
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message="Co khoang trang thua ben trong dau ngoac",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, m.start()),
                suggestion="Bo khoang trang sat dau ngoac",
            )
        )
    return issues


def _check_empty_paragraphs(doc: DocInfo, max_consecutive: int) -> list[Issue]:
    issues = []
    run_len = 0
    for p in doc.paragraphs:
        if not p.text.strip():
            run_len += 1
        else:
            if run_len > max_consecutive:
                issues.append(
                    Issue(
                        category=CATEGORY_TEXT,
                        severity=SEVERITY_WARNING,
                        message=f"Co nhieu doan trong lien tiep (toi da nen la {max_consecutive})",
                        paragraph=p.number,
                        excerpt=f"{run_len} doan trong lien tiep",
                        suggestion="Xoa bot cac doan trong thua",
                    )
                )
            run_len = 0
    return issues


# Cac hu tu hau nhu khong bao gio lap lai hop le -> lap lai la loi go.
# (Tranh bao nham tu lay tieng Viet nhu "xa xa", "xanh xanh".)
_REPEATABLE_TYPO_WORDS = {
    "các", "những", "và", "là", "của", "được", "đã", "sẽ", "cho", "với",
    "trong", "một", "này", "đó", "thì", "mà", "ở", "khi", "nếu", "vì",
    "the", "a", "an", "to", "of", "and", "is", "in",
}

# Viet tat thuong gap, khong tinh la ket thuc cau khi kiem tra viet hoa.
_ABBREVIATIONS = {
    "vv", "v.v", "tp", "ts", "ths", "th.s", "gs", "pgs", "cn", "kts",
    "ks", "bs", "tr", "stt", "no", "vd", "vdu", "tk", "tt", "nxb",
}


def _check_repeated_words(p: ParagraphInfo) -> list[Issue]:
    issues = []
    for m in re.finditer(r"(?<![^\W\d_])([^\W\d_]+)(\s+)(\1)(?![^\W\d_])", p.text, re.IGNORECASE):
        word = m.group(1).lower()
        if word not in _REPEATABLE_TYPO_WORDS:
            continue
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message=f"Lap tu lien tiep: '{m.group(1)} {m.group(3)}'",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, m.start()),
                suggestion="Xoa bot mot tu bi lap",
            )
        )
    return issues


def _check_sentence_capitalization(p: ParagraphInfo) -> list[Issue]:
    issues = []
    for m in re.finditer(r"([.!?])(\s+)(\w)", p.text):
        punct, _, ch = m.group(1), m.group(2), m.group(3)
        if not (ch.isalpha() and ch.islower()):
            continue
        # Bo qua dau "..." (ellipsis)
        start = m.start(1)
        if start >= 1 and p.text[start - 1] == ".":
            continue
        # Lay tu truoc dau cau de loai viet tat / so thu tu
        before = p.text[:start]
        wm = re.search(r"([^\s]+)$", before)
        token = wm.group(1).lower().rstrip(".") if wm else ""
        if token in _ABBREVIATIONS:
            continue
        if len(token) <= 1:  # vi du chu cai dau viet tat: "A."
            continue
        if token[-1:].isdigit():  # vi du so thu tu / so thap phan: "1." "3.14"
            continue
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message=f"Co the thieu viet hoa dau cau (sau dau '{punct}')",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, m.start(3)),
                suggestion=f"Viet hoa chu '{ch}'",
            )
        )
    return issues


def _check_double_hyphen(p: ParagraphInfo) -> list[Issue]:
    issues = []
    for m in re.finditer(r"--+", p.text):
        issues.append(
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message="Dung hai gach noi '--' (nen dung gach ngang '–' hoac '—')",
                paragraph=p.number,
                excerpt=_excerpt_around(p.text, m.start()),
                suggestion="Thay '--' bang gach ngang –",
            )
        )
    return issues


def _check_mixed_quotes(doc: DocInfo) -> list[Issue]:
    """Loi cap tai lieu: dung lan lon nhay thang (\") va nhay cong (“ ”)."""
    has_straight = False
    has_curly = False
    for p in doc.paragraphs:
        if '"' in p.text:
            has_straight = True
        if "\u201c" in p.text or "\u201d" in p.text:
            has_curly = True
    if has_straight and has_curly:
        return [
            Issue(
                category=CATEGORY_TEXT,
                severity=SEVERITY_WARNING,
                message="Tai lieu dung lan lon dau nhay thang (\") va nhay cong (“ ”)",
                paragraph=None,
                suggestion="Thong nhat mot kieu dau nhay trong toan tai lieu",
            )
        ]
    return []


def _check_placeholder(p: ParagraphInfo) -> list[Issue]:
    issues = []
    # Cac mau text "bo quen" thuong gap; giu danh sach hep de tranh bao nham.
    patterns = [
        (r"lorem ipsum", "Lorem ipsum"),
        (r"\bTODO\b", "TODO"),
        (r"\bFIXME\b", "FIXME"),
        (r"\[\.\.\.\]", "[...]"),
        (r"x{4,}", "chuoi x..."),
        (r"\bchen (?:noi dung|o day|vao day)\b", "ghi chu chen noi dung"),
    ]
    for pat, label in patterns:
        for m in re.finditer(pat, p.text, re.IGNORECASE):
            issues.append(
                Issue(
                    category=CATEGORY_TEXT,
                    severity=SEVERITY_WARNING,
                    message=f"Co the la chu con bo quen: '{m.group(0)}' ({label})",
                    paragraph=p.number,
                    excerpt=_excerpt_around(p.text, m.start()),
                    suggestion="Kiem tra va thay bang noi dung that",
                )
            )
    return issues


def check_text(doc: DocInfo, checks: dict, max_consecutive_empty: int, skip_math: bool = True) -> list[Issue]:
    issues: list[Issue] = []
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        # Bo qua cac doan cong thuc cho kiem tra dau cau (de bao nham)
        if skip_math and is_math_heavy(p.text):
            continue
        if checks.get("double_space"):
            issues += _check_double_space(p)
        if checks.get("space_before_punct"):
            issues += _check_space_before_punct(p)
        if checks.get("missing_space_after_punct"):
            issues += _check_missing_space_after_punct(p)
        if checks.get("trailing_space"):
            issues += _check_trailing_space(p)
        if checks.get("space_in_parens"):
            issues += _check_space_in_parens(p)
        if checks.get("repeated_words"):
            issues += _check_repeated_words(p)
        if checks.get("sentence_capitalization"):
            issues += _check_sentence_capitalization(p)
        if checks.get("double_hyphen"):
            issues += _check_double_hyphen(p)
        if checks.get("placeholder"):
            issues += _check_placeholder(p)

    if checks.get("mixed_quotes"):
        issues += _check_mixed_quotes(doc)

    if checks.get("empty_paragraphs"):
        issues += _check_empty_paragraphs(doc, max_consecutive_empty)

    return issues
