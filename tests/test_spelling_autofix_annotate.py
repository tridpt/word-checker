"""Test chinh ta, tu dong sua va xuat file co comment."""

import os

import config
from checker.annotate import annotate
from checker.autofix import autofix
from checker.document import load_document
from checker.formatting import check_formatting
from checker.runner import run_checks
from checker.spelling import check_spelling
from checker.textcheck import check_text


def test_spelling_detects_typo(make_doc):
    path = make_doc(["Toi muon chia se va bo xung kien thuc."])
    # "bo xung" -> "bo sung" co trong tu dien (khong dau van khop vi so sanh lowercase)
    doc = load_document(make_doc(["Day la cum bổ xung sai chinh ta."]))
    issues = check_spelling(doc)
    assert any("bổ xung" in it.message for it in issues)


def test_autofix_reduces_text_issues(make_doc, tmp_path):
    path = make_doc(["Cau co  cach doi , va loi ;tiep theo.   "])
    out = os.path.join(tmp_path, "fixed.docx")
    stats = autofix(path, out, max_consecutive_empty=config.MAX_CONSECUTIVE_EMPTY)
    assert stats["text_and_spelling_fixes"] > 0

    doc = load_document(out)
    issues = check_text(doc, config.TEXT_CHECKS, config.MAX_CONSECUTIVE_EMPTY)
    # sau khi sua khong con loi cach doi / cach truoc dau cau
    assert not any("cach doi" in it.message for it in issues)
    assert not any("truoc dau" in it.message for it in issues)


def test_autofix_does_not_change_original(make_doc, tmp_path):
    path = make_doc(["Cau co  cach doi."])
    before = os.path.getmtime(path)
    out = os.path.join(tmp_path, "fixed.docx")
    autofix(path, out)
    # file goc van con va khong bi ghi de
    assert os.path.exists(path)
    assert os.path.getmtime(path) == before


def test_annotate_adds_comments(make_doc, tmp_path):
    path = make_doc([{"text": "Doan sai font.", "font": "Arial"}])
    profile = config.get_profile(None)
    issues = run_checks(path, profile)
    out = os.path.join(tmp_path, "commented.docx")
    stats = annotate(path, out, issues)
    assert stats["comments_added"] >= 1
    assert os.path.exists(out)


def test_autofix_formatting(make_doc, tmp_path):
    # File dung font Arial 11 -> sau khi sua theo profile hanh_chinh phai het loi font/co chu
    path = make_doc([{"text": "Doan sai dinh dang.", "font": "Arial", "size": 11,
                      "align": None, "spacing": 1.0}])
    profile = config.get_profile(None)
    out = os.path.join(tmp_path, "fixed_fmt.docx")
    stats = autofix(path, out, fix_format=True, profile=profile)
    assert stats["format_fixes"] > 0

    from checker.formatting import check_formatting
    issues = check_formatting(load_document(out), profile)
    assert not any("Font khong dung" in it.message for it in issues)
    assert not any("Co chu khong dung" in it.message for it in issues)
