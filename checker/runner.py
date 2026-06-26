"""Logic chay kiem tra dung chung cho ca CLI lan web app."""

import config
from .document import load_document
from .formatting import check_formatting
from .headings import check_headings
from .spelling import check_spelling
from .textcheck import check_text


def run_checks(
    path,
    profile: dict,
    do_format: bool = True,
    do_text: bool = True,
    do_spelling: bool = True,
    do_llm_spelling: bool = False,
    do_headings: bool = True,
) -> list:
    """Doc tai lieu tu duong dan (hoac file-like) va tra ve danh sach Issue."""
    doc = load_document(path)
    issues = []
    if do_format:
        issues += check_formatting(doc, profile)
    if do_text:
        issues += check_text(doc, config.TEXT_CHECKS, config.MAX_CONSECUTIVE_EMPTY)
    if do_headings:
        issues += check_headings(doc, config.HEADING_CHECKS)
    if do_spelling:
        issues += check_spelling(doc)
    if do_llm_spelling:
        from .llm_spelling import check_spelling_llm
        issues += check_spelling_llm(doc)
    return issues
