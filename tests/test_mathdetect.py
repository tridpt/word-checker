"""Test nhan dien doan cong thuc va viec bo qua khi kiem tra."""

import config
from checker.document import load_document
from checker.mathdetect import is_math_heavy
from checker.textcheck import check_text


def test_detects_math_symbols():
    assert is_math_heavy("aℓ,i = h˜ft − hˆpre")
    assert is_math_heavy("Nk(stest) = TopK sim(h(si), h(stest)) .  (3.6)")


def test_plain_text_not_math():
    assert not is_math_heavy("Day la mot doan van xuoi binh thuong khong co cong thuc.")
    assert not is_math_heavy("Mo hinh BioBERT duoc tinh chinh cho tac vu SRL.")


def test_equation_label():
    assert is_math_heavy("P(yi = r) = P(yi = B-r) + P(yi = I-r).  (5.11)")


def test_check_text_skips_math(make_doc):
    # Dong cong thuc co "khoang trang truoc dau ," nhung khong nen bao loi
    path = make_doc(["sim(h(xi), h(xtest)) = θ , σ ∈ R"])
    issues = check_text(load_document(path), config.TEXT_CHECKS, 1, skip_math=True)
    assert issues == []
    # Khi tat skip_math thi co the bao loi
    issues2 = check_text(load_document(path), config.TEXT_CHECKS, 1, skip_math=False)
    assert len(issues2) >= 1
