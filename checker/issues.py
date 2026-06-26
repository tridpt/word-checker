"""Dinh nghia cau truc mot 'loi' (issue) duoc phat hien."""

from dataclasses import dataclass

# Muc do nghiem trong
SEVERITY_ERROR = "error"      # gan nhu chac chan sai, nen sua
SEVERITY_WARNING = "warning"  # nen xem lai

# Nhom loi
CATEGORY_FORMAT = "Dinh dang"
CATEGORY_TEXT = "Van ban"
CATEGORY_SPELLING = "Chinh ta"
CATEGORY_SPELLING_AI = "Chinh ta (AI)"
CATEGORY_HEADING = "Tieu de"
CATEGORY_LIMIT = "Gioi han"


@dataclass
class Issue:
    category: str          # CATEGORY_*
    severity: str          # SEVERITY_*
    message: str           # mo ta loi
    paragraph: int | None = None   # so thu tu doan (number), None neu loi cap tai lieu
    excerpt: str = ""      # trich doan van ban lien quan
    suggestion: str = ""   # goi y sua

    def location(self) -> str:
        if self.paragraph is None:
            return "Toan tai lieu"
        return f"Doan {self.paragraph}"

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "location": self.location(),
            "paragraph": self.paragraph,
            "excerpt": self.excerpt,
            "suggestion": self.suggestion,
        }
