"""Nhan dien doan/cau nhieu ky hieu toan (cong thuc) de bo qua khi kiem tra.

Tren tai lieu hoc thuat, cac dong cong thuc thuong dung font/co chu rieng va co
nhieu dau cach quanh ky hieu -> de bi bao loi nham. Module nay giup phat hien va
loai chung khoi mot so phep kiem tra.
"""

import re

# Cac ky hieu toan "manh": chi can xuat hien la coi nhu co cong thuc.
_MATH_SYMBOLS = set(
    "∑∏∫√≤≥≠≈≡∈∉∀∃∇∂∞±∓×÷⊤⊥∥·⋅∘→↦⇒⇔ℝℕℤℓ"
    "αβγδεζηθικλμνξπρσςτυφχψωΓΔΘΛΞΠΣΦΨΩ"
    "−⁻⁺₀₁₂₃₄₅₆₇₈₉ˆ˜⟨⟩‖"
)

# Mau so hieu phuong trinh o cuoi dong, vi du "(4.1)" hoac "(3.12)".
_EQ_LABEL = re.compile(r"\(\d+\.\d+[a-z]?\)\s*$")


def is_math_heavy(text: str) -> bool:
    t = text.strip()
    if not t:
        return False

    # 1) Co ky hieu toan manh -> chac chan la cong thuc
    if any(ch in _MATH_SYMBOLS for ch in t):
        return True

    # 2) Co so hieu phuong trinh o cuoi dong
    if _EQ_LABEL.search(t):
        return True

    # 3) Ty le token "kieu toan" cao (bien mot chu cai, ham f(x), chi so x_i,
    #    cac toan tu = + - * / ^ ( ))
    tokens = t.split()
    if len(tokens) >= 3:
        mathish = 0
        for tok in tokens:
            if re.fullmatch(r"[A-Za-z]", tok):                 # bien mot chu cai
                mathish += 1
            elif re.search(r"[A-Za-z]\w*\([^)]*\)", tok):      # ham f(x), h(xi)
                mathish += 1
            elif re.search(r"[A-Za-z]_?\d", tok):              # chi so: x1, s_i
                mathish += 1
            elif re.fullmatch(r"[=+\-*/^()|]+", tok):          # toan tu thuan
                mathish += 1
        if mathish / len(tokens) >= 0.35:
            return True

    return False
