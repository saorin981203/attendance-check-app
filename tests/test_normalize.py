from app.normalize import apply_replacements, normalize_name


def test_normalize_name_removes_spaces_and_symbols():
    assert normalize_name("髙 橋・太郎") == "髙橋太郎"


def test_apply_replacements():
    replacements = {"髙橋太郎": "高橋太郎"}
    assert apply_replacements("髙橋太郎", replacements) == "高橋太郎"
