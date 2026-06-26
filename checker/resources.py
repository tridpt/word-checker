"""Phan giai duong dan tai nguyen, chay duoc ca khi dev lan khi da dong goi (.exe).

Khi chay tu file .exe do PyInstaller tao, cac file du lieu (web/, dictionaries/)
duoc giai nen vao thu muc tam sys._MEIPASS. Khi chay binh thuong thi nam o thu
muc goc du an.
"""

import os
import sys


def base_dir() -> str:
    if getattr(sys, "frozen", False):
        # Dang chay tu ban dong goi PyInstaller
        return getattr(sys, "_MEIPASS", os.path.abspath("."))
    # Dang chay binh thuong: thu muc goc du an (cha cua package 'checker')
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resource_path(*parts: str) -> str:
    return os.path.join(base_dir(), *parts)
