"""Chuyen doi file .doc (Word cu) sang .docx de xu ly.

python-docx chi doc duoc .docx. File .doc cu can chuyen doi truoc. Module nay
thu lan luot:
  1) Microsoft Word qua COM (win32com) - neu may co cai Word (chi tren Windows).
  2) LibreOffice (soffice) - neu co cai LibreOffice (da nen tang).

Neu khong co cong cu nao, nem ConversionError kem huong dan cho nguoi dung.
"""

import os
import shutil
import subprocess
import tempfile


class ConversionError(Exception):
    """Loi khi khong the chuyen doi .doc -> .docx."""


def _convert_with_word(src: str, out_dir: str) -> str | None:
    """Dung Microsoft Word qua COM (chi Windows, can cai Word). Tra ve path hoac None."""
    try:
        import win32com.client  # type: ignore
    except Exception:
        return None

    word = None
    src_abs = os.path.abspath(src)
    out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(src))[0] + ".docx")
    try:
        import pythoncom  # type: ignore
        pythoncom.CoInitialize()
    except Exception:
        pass
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(src_abs, ReadOnly=True)
        # 16 = wdFormatXMLDocument (.docx)
        doc.SaveAs2(os.path.abspath(out_path), FileFormat=16)
        doc.Close(SaveChanges=False)
        return out_path if os.path.exists(out_path) else None
    except Exception:
        return None
    finally:
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass


def _find_soffice() -> str | None:
    """Tim duong dan toi LibreOffice/soffice."""
    for name in ("soffice", "soffice.exe", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    # Cac vi tri cai dat pho bien tren Windows
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _convert_with_soffice(src: str, out_dir: str) -> str | None:
    """Dung LibreOffice o che do headless. Tra ve path hoac None."""
    soffice = _find_soffice()
    if not soffice:
        return None
    src_abs = os.path.abspath(src)
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "docx", "--outdir", out_dir, src_abs],
            check=True,
            capture_output=True,
            timeout=120,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return None
    out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(src))[0] + ".docx")
    return out_path if os.path.exists(out_path) else None


def convert_doc_to_docx(src: str, out_dir: str | None = None) -> str:
    """Chuyen .doc sang .docx, tra ve duong dan file .docx moi.

    Neu khong co cong cu chuyen doi (Word/LibreOffice), nem ConversionError.
    """
    if out_dir is None:
        out_dir = tempfile.mkdtemp(prefix="wordcheck_")

    for converter in (_convert_with_word, _convert_with_soffice):
        out = converter(src, out_dir)
        if out:
            return out

    raise ConversionError(
        "Khong chuyen doi duoc file .doc. Can cai Microsoft Word hoac LibreOffice, "
        "hoac tu mo file bang Word roi 'Save As' sang dinh dang .docx."
    )


def ensure_docx(path: str) -> tuple[str, bool]:
    """Dam bao co file .docx de xu ly.

    Tra ve (docx_path, is_temp). Neu goc da la .docx thi tra ve (path, False).
    Neu la .doc thi chuyen doi va tra ve (path_moi, True) - nguoi goi nen xoa file
    tam khi dung xong.
    """
    lower = path.lower()
    if lower.endswith(".docx"):
        return path, False
    if lower.endswith(".doc"):
        out = convert_doc_to_docx(path)
        return out, True
    raise ConversionError("Chi ho tro file .doc hoac .docx.")
