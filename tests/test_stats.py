"""Test thong ke tai lieu."""

from checker.document import load_document
from checker.stats import compute_stats


def test_basic_stats(make_doc):
    path = make_doc([
        "Mot hai ba bon nam.",   # 5 tu
        "Sau bay tam.",          # 3 tu
    ])
    stats = compute_stats(load_document(path))
    assert stats["words"] == 8
    assert stats["paragraphs"] == 2
    assert stats["reading_minutes"] >= 1
    assert stats["estimated_pages"] >= 1


def test_empty_doc(make_doc):
    path = make_doc([])
    stats = compute_stats(load_document(path))
    assert stats["words"] == 0
    assert stats["paragraphs"] == 0
    assert stats["reading_minutes"] == 0
