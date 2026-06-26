"""Kiem tra chinh ta / ngu phap tieng Viet bang LLM (tuy chon).

Tinh nang nay TAT mac dinh, chi bat khi da cau hinh LLM_API_KEY (xem config.py /
file .env). Goi mo hinh theo chuan OpenAI-compatible. Gui cac doan van da danh so
va yeu cau mo hinh tra ve danh sach loi dang JSON.

Luu y: ket qua tu AI mang tinh GOI Y, co the sai. Vi vay cac loi nay duoc danh
muc do "warning" (canh bao), khong phai "error".
"""

import json
import re

import httpx

import config
from .document import DocInfo
from .issues import CATEGORY_SPELLING_AI, SEVERITY_WARNING, Issue


class LLMError(Exception):
    pass


# So ky tu toi da moi lan goi (gom nhieu doan). Tranh prompt qua dai.
_CHUNK_CHARS = 3500

_SYSTEM = (
    "Ban la bien tap vien tieng Viet. Nhiem vu: tim loi CHINH TA va loi GO DAU "
    "trong cac doan van duoc danh so. Chi bao loi chac chan (sai chinh ta, sai "
    "dau cau tu, thieu/thua dau thanh dieu). KHONG goi y ve van phong, dau cham "
    "cau hay cach dien dat. Neu khong co loi, tra ve mang rong."
)

_INSTRUCT = (
    "Tra ve DUY NHAT mot mang JSON, moi phan tu co dang:\n"
    '{"p": <so doan>, "wrong": "<cum tu sai>", "correct": "<cum tu dung>", "note": "<ly do ngan>"}\n'
    "Khong them giai thich nao khac ngoai mang JSON."
)


def _chunks(paragraphs):
    """Chia cac (number, text) thanh tung lo theo gioi han ky tu."""
    chunk, size = [], 0
    for num, text in paragraphs:
        line_len = len(text) + 8
        if chunk and size + line_len > _CHUNK_CHARS:
            yield chunk
            chunk, size = [], 0
        chunk.append((num, text))
        size += line_len
    if chunk:
        yield chunk


def _extract_json_array(content: str):
    """Trich mang JSON tu phan hoi (co the bi bao boi ```json ... ```)."""
    content = content.strip()
    content = re.sub(r"^```(?:json)?", "", content).strip()
    content = re.sub(r"```$", "", content).strip()
    m = re.search(r"\[.*\]", content, re.DOTALL)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return []


def _call_llm(prompt: str) -> str:
    url = f"{config.LLM['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.LLM['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.LLM["model"],
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": 1500,
    }
    try:
        resp = httpx.post(url, headers=headers, json=payload, timeout=90)
    except httpx.HTTPError as e:
        raise LLMError(f"Loi ket noi toi LLM: {e}") from e
    if resp.status_code != 200:
        raise LLMError(f"LLM tra ve {resp.status_code}: {resp.text[:200]}")
    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise LLMError("Phan hoi LLM khong dung dinh dang.") from e


def check_spelling_llm(doc: DocInfo) -> list[Issue]:
    if not config.llm_enabled():
        raise LLMError(
            "Chua cau hinh LLM_API_KEY. Dat trong file .env hoac bien moi truong "
            "de dung kiem tra chinh ta bang AI."
        )

    paragraphs = [(p.number, p.text.strip()) for p in doc.paragraphs if p.text.strip()]
    text_by_num = {num: text for num, text in paragraphs}
    issues: list[Issue] = []

    for chunk in _chunks(paragraphs):
        numbered = "\n".join(f"[{num}] {text}" for num, text in chunk)
        prompt = f"{_INSTRUCT}\n\nCac doan can kiem tra:\n{numbered}"
        content = _call_llm(prompt)
        for item in _extract_json_array(content):
            try:
                num = int(item.get("p"))
                wrong = str(item.get("wrong", "")).strip()
                correct = str(item.get("correct", "")).strip()
                note = str(item.get("note", "")).strip()
            except (TypeError, ValueError):
                continue
            if not wrong or num not in text_by_num:
                continue
            # Chi nhan loi neu cum tu sai that su xuat hien trong doan (chong ao giac)
            if wrong not in text_by_num[num]:
                continue
            suggestion = f"Co the la '{correct}'" if correct else ""
            if note:
                suggestion = (suggestion + f" ({note})").strip()
            issues.append(
                Issue(
                    category=CATEGORY_SPELLING_AI,
                    severity=SEVERITY_WARNING,
                    message=f"AI phat hien co the sai: '{wrong}'",
                    paragraph=num,
                    excerpt=wrong,
                    suggestion=suggestion,
                )
            )
    return issues
