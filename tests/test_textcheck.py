"""Test cac kiem tra loi co hoc van ban."""

import config
from checker.document import load_document
from checker.textcheck import check_text


def _messages(path):
    doc = load_document(path)
    issues = check_text(doc, config.TEXT_CHECKS, config.MAX_CONSECUTIVE_EMPTY)
    return [it.message for it in issues]


def test_double_space(make_doc):
    path = make_doc(["Cau nay co  cach doi giua cac tu."])
    assert any("cach doi" in m for m in _messages(path))


def test_space_before_punct(make_doc):
    path = make_doc(["Day la cau loi , co dau cach truoc dau phay."])
    assert any("truoc dau" in m for m in _messages(path))


def test_missing_space_after_punct(make_doc):
    path = make_doc(["Mot,hai,ba khong co dau cach."])
    assert any("Thieu dau cach sau" in m for m in _messages(path))


def test_missing_space_not_flag_numbers(make_doc):
    # 3,14 va 10:30 khong nen bi bao loi
    path = make_doc(["Gia tri la 3,14 luc 10:30 hom nay."])
    assert not any("Thieu dau cach sau" in m for m in _messages(path))


def test_repeated_word(make_doc):
    path = make_doc(["Day la các các van de can xem."])
    assert any("Lap tu" in m for m in _messages(path))


def test_repeated_word_ignores_reduplication(make_doc):
    # tu lay "xa xa" khong nam trong danh sach hu tu -> khong bao loi
    path = make_doc(["Phia xa xa co mot ngoi nha."])
    assert not any("Lap tu" in m for m in _messages(path))


def test_sentence_capitalization(make_doc):
    path = make_doc(["Cau dau tien. cau hai khong viet hoa."])
    assert any("viet hoa" in m for m in _messages(path))


def test_sentence_cap_ignores_abbrev_number(make_doc):
    path = make_doc(["Muc 1. noi dung muc mot."])
    # sau so thu tu "1." khong nen bao thieu viet hoa
    assert not any("viet hoa" in m for m in _messages(path))


def test_double_hyphen(make_doc):
    path = make_doc(["Cum tu -- gach doi can sua."])
    assert any("hai gach noi" in m for m in _messages(path))


def test_mixed_quotes(make_doc):
    path = make_doc(['Cau co nhay thang "abc" va nhay cong \u201cxyz\u201d.'])
    assert any("lan lon" in m for m in _messages(path))


def test_no_mixed_quotes_when_consistent(make_doc):
    path = make_doc(['Cau chi dung nhay thang "abc" thoi.'])
    assert not any("lan lon" in m for m in _messages(path))


def test_placeholder_todo(make_doc):
    path = make_doc(["Phan nay TODO se viet sau."])
    assert any("bo quen" in m for m in _messages(path))


def test_placeholder_lorem(make_doc):
    path = make_doc(["Lorem ipsum dolor sit amet."])
    assert any("bo quen" in m for m in _messages(path))
