"""Cau hinh quy chuan dinh dang cho file Word.

Chinh sua cac gia tri o day de phu hop voi yeu cau cua truong/cong ty cua ban.
Mac dinh tuan theo quy chuan van ban hanh chinh pho bien tai Viet Nam:
Times New Roman, co 13-14, gian dong 1.5, canh deu hai ben.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # nap .env o thu muc lam viec neu co
except Exception:
    pass


# ===== Cau hinh LLM (tuy chon) cho kiem tra chinh ta bang AI =====
# Theo chuan OpenAI-compatible. De trong API key thi tinh nang nay TAT.
# Vi du Groq (free): https://console.groq.com
LLM = {
    "base_url": os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
    "api_key": os.getenv("LLM_API_KEY", ""),
    "model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
}


def llm_enabled() -> bool:
    return bool(LLM["api_key"])


# Profile dinh dang chuan
FORMAT_PROFILE = {
    # Ten font cho phep o phan than bai (body). Co the liet ke nhieu font.
    "body_font_names": ["Times New Roman"],
    # Cac co chu cho phep o body (don vi: point). Vi du 13 hoac 14.
    "body_font_sizes": [13, 14],
    # Gian dong yeu cau (1.5 = 1.5 lines). De None neu khong kiem tra.
    "line_spacing": 1.5,
    # Sai so cho phep khi so sanh gian dong.
    "line_spacing_tolerance": 0.05,
    # Canh le yeu cau cho body: "justify" | "left" | "center" | "right" | None
    "body_alignment": "justify",
    # Le trang yeu cau (don vi: cm). De None de bo qua tung canh.
    "margins_cm": {
        "top": 2.0,
        "bottom": 2.0,
        "left": 3.0,
        "right": 2.0,
    },
    # Sai so cho phep khi so sanh le trang (cm).
    "margin_tolerance_cm": 0.2,
    # Thut le dong dau cua doan (cm). De None de bo qua. Vi du 1.0 hoac 1.27.
    "first_line_indent_cm": None,
    "first_line_indent_tolerance_cm": 0.2,
    # Khoang cach truoc/sau doan (point). De None de bo qua. Vi du 0 hoac 6.
    "space_before_pt": None,
    "space_after_pt": None,
    "paragraph_spacing_tolerance_pt": 1.0,
}

# Cac profile quy chuan khac nhau. Chon bang tham so --profile tren dong lenh.
# "hanh_chinh" la mac dinh (chinh la FORMAT_PROFILE o tren).
PROFILES = {
    # Van ban hanh chinh (Times New Roman 13-14, gian 1.5, canh deu)
    "hanh_chinh": FORMAT_PROFILE,

    # Luan van / khoa luan: thuong Times New Roman 13, gian 1.5, le trai rong de dong quyen
    "luan_van": {
        "body_font_names": ["Times New Roman"],
        "body_font_sizes": [13],
        "line_spacing": 1.5,
        "line_spacing_tolerance": 0.05,
        "body_alignment": "justify",
        "margins_cm": {"top": 2.0, "bottom": 2.0, "left": 3.5, "right": 2.0},
        "margin_tolerance_cm": 0.2,
    },

    # Bao cao cong ty kieu hien dai: cho phep Arial/Calibri, co 11-12, gian 1.15
    "cong_ty": {
        "body_font_names": ["Arial", "Calibri", "Times New Roman"],
        "body_font_sizes": [11, 12],
        "line_spacing": 1.15,
        "line_spacing_tolerance": 0.05,
        "body_alignment": None,
        "margins_cm": {"top": 2.0, "bottom": 2.0, "left": 2.0, "right": 2.0},
        "margin_tolerance_cm": 0.3,
    },
}

DEFAULT_PROFILE = "hanh_chinh"


def get_profile(name: str | None) -> dict:
    """Lay profile theo ten; neu None hoac khong ton tai thi dung mac dinh."""
    if not name:
        return PROFILES[DEFAULT_PROFILE]
    return PROFILES.get(name, PROFILES[DEFAULT_PROFILE])


# Kiem tra loi co hoc van ban (bat/tat tung loai)
TEXT_CHECKS = {
    "double_space": True,        # cach doi (nhieu dau cach lien tiep)
    "space_before_punct": True,  # dau cach thua truoc , . ; : ! ?
    "missing_space_after_punct": True,  # thieu dau cach sau , ; :
    "trailing_space": True,      # khoang trang cuoi doan
    "empty_paragraphs": True,    # nhieu doan trong lien tiep
    "space_in_parens": True,     # khoang trang ben trong ( )
    "repeated_words": True,      # lap tu lien tiep (vd: "cac cac")
    "sentence_capitalization": True,  # viet hoa dau cau sau . ! ?
    "double_hyphen": True,       # dung '--' thay vi gach ngang
    "mixed_quotes": True,        # lan lon nhay thang va nhay cong
    "placeholder": True,         # chu con bo quen (lorem ipsum, TODO, [...]...)
}

# Gioi han so tu / so trang (None = khong kiem tra). Co the override bang CLI.
LIMITS = {
    "min_words": None,
    "max_words": None,
    "max_pages": None,
}

# So doan trong lien tiep toi da cho phep truoc khi bao loi.
MAX_CONSECUTIVE_EMPTY = 1

# Bo qua cac doan nhieu ky hieu toan (cong thuc) khi kiem tra font/co chu/dau cau,
# de tranh bao nham tren tai lieu hoc thuat. Dat False de kiem ca cong thuc.
SKIP_MATH = True

# Kiem tra tieu de muc va danh so de muc.
HEADING_CHECKS = {
    "level_jump": True,           # nhay cap tieu de (Heading 1 -> Heading 3)
    "numbering_sequence": True,   # danh so de muc khong lien tuc
}
