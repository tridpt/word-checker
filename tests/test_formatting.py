"""Test kiem tra dinh dang."""

import config
from checker.document import load_document
from checker.formatting import check_formatting


def _messages(path, profile=None):
    doc = load_document(path)
    issues = check_formatting(doc, profile or config.get_profile(None))
    return [it.message for it in issues]


def test_wrong_font(make_doc):
    path = make_doc([{"text": "Doan sai font.", "font": "Arial"}])
    assert any("Font khong dung" in m for m in _messages(path))


def test_wrong_size(make_doc):
    path = make_doc([{"text": "Doan sai co chu.", "size": 11}])
    assert any("Co chu khong dung" in m for m in _messages(path))


def test_correct_format_no_font_size_issue(make_doc):
    path = make_doc([{"text": "Doan dung chuan.", "font": "Times New Roman", "size": 14}])
    msgs = _messages(path)
    assert not any("Font khong dung" in m for m in msgs)
    assert not any("Co chu khong dung" in m for m in msgs)


def test_inconsistent_fonts(make_doc):
    path = make_doc([
        {"text": "Doan mot.", "font": "Times New Roman"},
        {"text": "Doan hai.", "font": "Arial"},
    ])
    assert any("nhieu font khac nhau" in m for m in _messages(path))
