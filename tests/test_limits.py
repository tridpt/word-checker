"""Test gioi han so tu / so trang."""

from checker.document import load_document
from checker.limits import check_limits


def _msgs(path, limits):
    return [it.message for it in check_limits(load_document(path), limits)]


def test_max_words_exceeded(make_doc):
    path = make_doc(["mot hai ba bon nam sau bay tam chin muoi"])  # 10 tu
    assert any("Vuot gioi han so tu" in m for m in _msgs(path, {"max_words": 5}))


def test_min_words_not_met(make_doc):
    path = make_doc(["mot hai ba"])  # 3 tu
    assert any("Thieu so tu" in m for m in _msgs(path, {"min_words": 10}))


def test_within_limits_no_issue(make_doc):
    path = make_doc(["mot hai ba bon nam"])  # 5 tu
    assert _msgs(path, {"min_words": 1, "max_words": 100}) == []


def test_no_limits_no_issue(make_doc):
    path = make_doc(["mot hai ba"])
    assert check_limits(load_document(path), None) == []
