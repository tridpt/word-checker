"""Test hoc quy chuan tu file mau."""

from checker.learn_profile import learn_profile


def test_learn_basic(make_doc):
    ref = make_doc([
        {"text": "Doan mot theo chuan.", "font": "Arial", "size": 12},
        {"text": "Doan hai theo chuan.", "font": "Arial", "size": 12},
        {"text": "Doan ba theo chuan.", "font": "Arial", "size": 12},
    ])
    profile = learn_profile(ref)
    assert profile["body_font_names"] == ["Arial"]
    assert profile["body_font_sizes"] == [12]
    assert profile["body_alignment"] == "justify"
    assert abs(profile["line_spacing"] - 1.5) < 0.01


def test_learn_picks_dominant_font(make_doc):
    # 3 doan Times, 1 doan Arial -> font chuan la Times New Roman
    ref = make_doc([
        {"text": "A.", "font": "Times New Roman", "size": 13},
        {"text": "B.", "font": "Times New Roman", "size": 13},
        {"text": "C.", "font": "Times New Roman", "size": 13},
        {"text": "D.", "font": "Arial", "size": 13},
    ])
    profile = learn_profile(ref)
    assert "Times New Roman" in profile["body_font_names"]
    assert profile["body_font_sizes"] == [13]


def test_learned_profile_usable_by_formatter(make_doc):
    import config
    from checker.document import load_document
    from checker.formatting import check_formatting

    ref = make_doc([{"text": "Chuan.", "font": "Arial", "size": 12}])
    profile = learn_profile(ref)

    # File dung font Times 14 se vi pham profile da hoc (Arial 12)
    target = make_doc([{"text": "Sai chuan.", "font": "Times New Roman", "size": 14}])
    issues = check_formatting(load_document(target), profile)
    assert any("Font khong dung" in it.message for it in issues)
