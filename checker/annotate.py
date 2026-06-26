"""Xuat ban sao .docx co chu thich (comment) tai vi tri loi.

Mo file ket qua bang Microsoft Word se thay cac comment hien o le phai, gom toan
bo loi cua tung doan. Loi cap tai lieu (le trang, font khong dong nhat...) duoc
gom vao mot comment o dau tai lieu.
"""

from collections import defaultdict

from docx import Document

from .issues import Issue


def _format_issue_line(it: Issue) -> str:
    line = f"[{it.category}] {it.message}"
    if it.suggestion:
        line += f" -> {it.suggestion}"
    return line


def annotate(src_path: str, out_path: str, issues: list[Issue]) -> dict:
    """Them comment vao file va luu ra out_path. Tra ve thong ke."""
    document = Document(src_path)

    # Tai tao cach danh so doan (number) giong load_document: dem doan khong rong.
    para_by_number = {}
    number = 0
    for p in document.paragraphs:
        if p.text.strip():
            number += 1
            para_by_number[number] = p

    grouped: dict[int, list[Issue]] = defaultdict(list)
    doc_level: list[Issue] = []
    for it in issues:
        if it.paragraph is None:
            doc_level.append(it)
        else:
            grouped[it.paragraph].append(it)

    added = 0

    # Comment cho tung doan
    for num, its in sorted(grouped.items()):
        p = para_by_number.get(num)
        if p is None or not p.runs:
            continue
        text = "\n".join(_format_issue_line(it) for it in its)
        try:
            document.add_comment(p.runs, text=text, author="Word Checker", initials="WC")
            added += 1
        except Exception:
            continue

    # Comment gom cac loi cap tai lieu, dat o doan dau tien
    if doc_level:
        first = para_by_number.get(1)
        if first is not None and first.runs:
            text = "LOI CAP TAI LIEU:\n" + "\n".join(_format_issue_line(it) for it in doc_level)
            try:
                document.add_comment(first.runs, text=text, author="Word Checker", initials="WC")
                added += 1
            except Exception:
                pass

    document.save(out_path)
    return {"comments_added": added, "out_path": out_path}
