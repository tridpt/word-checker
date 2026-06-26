"""Test xuat bao cao PDF."""

import os

import config
from checker.document import load_document
from checker.pdf_report import write_pdf
from checker.runner import run_checks
from checker.spelling import check_spelling
from checker.stats import compute_stats


def test_pdf_created(make_doc, tmp_path):
    path = make_doc([{"text": "Doan sai font.", "font": "Arial"}])
    issues = run_checks(path, config.get_profile(None))
    stats = compute_stats(load_document(path))
    out = os.path.join(tmp_path, "report.pdf")
    write_pdf(out, path, issues, stats)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 500
    with open(out, "rb") as fh:
        assert fh.read(4) == b"%PDF"


def test_pdf_no_issues(make_doc, tmp_path):
    path = make_doc([{"text": "Doan chuan.", "font": "Times New Roman", "size": 14}])
    out = os.path.join(tmp_path, "ok.pdf")
    write_pdf(out, path, [], compute_stats(load_document(path)))
    assert os.path.exists(out)


def test_new_typos_detected(make_doc):
    # Cac loi vua bo sung vao tu dien
    for wrong in ["cập nhập", "nổ lực", "lãng mạng"]:
        doc = load_document(make_doc([f"Cau co tu {wrong} trong do."]))
        msgs = [it.message for it in check_spelling(doc)]
        assert any(wrong in m for m in msgs), wrong
