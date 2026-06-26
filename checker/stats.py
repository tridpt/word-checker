"""Thong ke nhanh ve tai lieu: so tu, so doan, so tieu de, thoi gian doc..."""

import math

from .document import DocInfo

# Toc do doc trung binh (tu/phut) va so tu uoc tinh tren mot trang A4.
_WORDS_PER_MINUTE = 200
_WORDS_PER_PAGE = 350


def compute_stats(doc: DocInfo) -> dict:
    word_count = 0
    char_count = 0
    para_count = 0
    heading_count = 0

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        para_count += 1
        if p.is_heading:
            heading_count += 1
        word_count += len(text.split())
        char_count += len(text)

    reading_min = max(1, math.ceil(word_count / _WORDS_PER_MINUTE)) if word_count else 0
    pages = max(1, math.ceil(word_count / _WORDS_PER_PAGE)) if word_count else 0

    return {
        "words": word_count,
        "chars": char_count,
        "paragraphs": para_count,
        "headings": heading_count,
        "reading_minutes": reading_min,
        "estimated_pages": pages,
    }
