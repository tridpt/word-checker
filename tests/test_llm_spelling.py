"""Test module kiem tra chinh ta bang LLM (mock, khong goi mang that)."""

import json

import config
from checker import llm_spelling
from checker.document import load_document
from checker.issues import CATEGORY_SPELLING_AI


def test_extract_json_array_plain():
    arr = llm_spelling._extract_json_array('[{"p":1,"wrong":"a","correct":"b"}]')
    assert arr == [{"p": 1, "wrong": "a", "correct": "b"}]


def test_extract_json_array_with_code_fence():
    content = "```json\n[{\"p\":2,\"wrong\":\"x\",\"correct\":\"y\"}]\n```"
    arr = llm_spelling._extract_json_array(content)
    assert arr and arr[0]["p"] == 2


def test_extract_json_array_garbage():
    assert llm_spelling._extract_json_array("khong co json o day") == []


def test_disabled_raises(monkeypatch, make_doc):
    monkeypatch.setattr(config, "LLM", {**config.LLM, "api_key": ""})
    doc = load_document(make_doc(["Mot doan van."]))
    try:
        llm_spelling.check_spelling_llm(doc)
        assert False, "phai raise LLMError khi chua cau hinh"
    except llm_spelling.LLMError:
        pass


def test_maps_llm_output_to_issues(monkeypatch, make_doc):
    # Bat LLM (gia)
    monkeypatch.setattr(config, "LLM", {**config.LLM, "api_key": "fake-key"})

    path = make_doc(["Toi di hoc va lam bai tap chuyen can."])
    doc = load_document(path)

    # cum tu "lam bai" co that trong doan 1 -> phai duoc nhan
    fake_response = json.dumps([
        {"p": 1, "wrong": "lam bai", "correct": "làm bài", "note": "thieu dau"},
        {"p": 1, "wrong": "khong-ton-tai", "correct": "abc"},  # khong co trong doan -> bo
        {"p": 99, "wrong": "lam bai", "correct": "x"},          # so doan sai -> bo
    ])
    monkeypatch.setattr(llm_spelling, "_call_llm", lambda prompt: fake_response)

    issues = llm_spelling.check_spelling_llm(doc)
    assert len(issues) == 1
    it = issues[0]
    assert it.category == CATEGORY_SPELLING_AI
    assert it.excerpt == "lam bai"
    assert "làm bài" in it.suggestion
