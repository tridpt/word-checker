"""Tu dong sua mot so loi co hoc va loi chinh ta, luu ra file .docx moi.

Nguyen tac an toan:
- Khong ghi de file goc; luu ra file moi (mac dinh them hau to '_fixed').
- Sua o cap 'run' de giu nguyen dinh dang (font, mau, dam/nghieng...).
- Chi sua nhung loi chac chan (whitespace, dau cau, loi chinh ta trong tu dien).
"""

import re

from docx import Document

from .spelling import load_typo_dict

_PUNCT_NO_SPACE_BEFORE = ",.;:!?)"


def _fix_run_text(text: str, typos: dict[str, str]) -> tuple[str, int]:
    """Sua loi co hoc + chinh ta trong text cua mot run. Tra ve (text_moi, so_loi_sua)."""
    count = 0

    # 1) Bo dau cach truoc dau cau
    new, n = re.subn(r"[ \t]+([" + re.escape(_PUNCT_NO_SPACE_BEFORE) + r"])", r"\1", text)
    count += n
    text = new

    # 2) Gop nhieu dau cach lien tiep thanh mot
    new, n = re.subn(r"  +", " ", text)
    count += n
    text = new

    # 3) Them dau cach sau , ; : neu thieu (tru giua hai chu so)
    def _add_space(m):
        return m.group(1) + " "

    new, n = re.subn(r"([,;:])(?=[^\s\d])", _add_space, text)
    # tranh dong cham truong hop so:so (gio) -> dieu kien tren da loai chu so phia sau
    count += n
    text = new

    # 4) Sua loi chinh ta theo tu dien (khop ca tu, khong phan biet hoa/thuong)
    for wrong, right in typos.items():
        pattern = re.compile(r"(?<!\w)(" + re.escape(wrong) + r")(?!\w)", re.IGNORECASE | re.UNICODE)

        def _repl(m):
            nonlocal count
            count += 1
            return _match_case(m.group(1), right)

        text = pattern.sub(_repl, text)

    return text, count


def _match_case(found: str, replacement: str) -> str:
    """Giu kieu viet hoa: neu tu sai viet hoa chu cai dau thi tu dung cung vay."""
    if found[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _remove_extra_empty_paragraphs(document, max_consecutive: int) -> int:
    """Xoa cac doan trong lien tiep vuot qua gioi han. Tra ve so doan da xoa."""
    removed = 0
    run_len = 0
    to_delete = []
    for p in document.paragraphs:
        if not p.text.strip():
            run_len += 1
            if run_len > max_consecutive:
                to_delete.append(p)
        else:
            run_len = 0
    for p in to_delete:
        el = p._element
        el.getparent().remove(el)
        removed += 1
    return removed


def autofix(
    src_path: str,
    out_path: str,
    max_consecutive_empty: int = 1,
    fix_spelling: bool = True,
) -> dict:
    """Sua file va luu ra out_path. Tra ve thong ke so loi da sua."""
    document = Document(src_path)
    typos = load_typo_dict() if fix_spelling else {}

    # Sua cac doan cuoi cau bi thua khoang trang: xu ly o run cuoi cung
    text_fixes = 0
    for p in document.paragraphs:
        runs = p.runs
        for i, run in enumerate(runs):
            new_text, n = _fix_run_text(run.text, typos)
            # Cat khoang trang cuoi doan: chi ap dung cho run cuoi cung co noi dung
            if i == len(runs) - 1:
                new_text = new_text.rstrip()
            if new_text != run.text:
                run.text = new_text
            text_fixes += n

    empty_removed = _remove_extra_empty_paragraphs(document, max_consecutive_empty)

    document.save(out_path)
    return {
        "text_and_spelling_fixes": text_fixes,
        "empty_paragraphs_removed": empty_removed,
        "out_path": out_path,
    }
