"""Test tinh toan ven cua tu dien chinh ta va logic ensure_docx cho file .doc."""

import os

import pytest

from checker.convert import ConversionError, ensure_docx
from checker.spelling import load_typo_dict


def test_dictionary_has_no_identity_pairs():
    """Khong cap nao co ve trai == ve phai (se bao nham tu dung)."""
    typos = load_typo_dict()
    identical = [(w, r) for w, r in typos.items() if w == r.lower()]
    assert not identical, f"Cap trung (bao nham): {identical}"


def test_dictionary_is_reasonably_sized():
    """Tu dien co du so cap sau khi mo rong."""
    typos = load_typo_dict()
    assert len(typos) >= 100


def test_ensure_docx_passthrough_for_docx(make_doc):
    """File .docx duoc tra ve nguyen ven, khong tao file tam."""
    path = make_doc(["Mot doan van ban."])
    out, is_temp = ensure_docx(path)
    assert out == path
    assert is_temp is False


def test_ensure_docx_rejects_other_extensions(tmp_path):
    other = os.path.join(tmp_path, "file.txt")
    with open(other, "w", encoding="utf-8") as f:
        f.write("khong phai word")
    with pytest.raises(ConversionError):
        ensure_docx(other)
