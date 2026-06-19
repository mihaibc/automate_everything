

def test_check_markdown_accepts_valid_links(tmp_path, monkeypatch, load_script):
    checker = load_script("scripts/check_markdown.py")
    (tmp_path / "README.md").write_text("# Title\n\n[Section](#section)\n\n## Section\n", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    assert checker.main() == 0


def test_check_markdown_reports_broken_links(tmp_path, monkeypatch, capsys, load_script):
    checker = load_script("scripts/check_markdown.py")
    (tmp_path / "README.md").write_text("# Title\n\n[Missing](missing.md)\n", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    assert checker.main() == 1
    assert "broken link" in capsys.readouterr().out


def test_check_markdown_reports_missing_anchor(tmp_path, monkeypatch, capsys, load_script):
    checker = load_script("scripts/check_markdown.py")
    (tmp_path / "README.md").write_text("# Title\n\n[Nope](#nope)\n", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    assert checker.main() == 1
    assert "missing anchor" in capsys.readouterr().out


def test_check_no_markers_accepts_clean_tree(tmp_path, monkeypatch, load_script):
    checker = load_script("scripts/check_no_markers.py")
    (tmp_path / "README.md").write_text("clean text\n", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    assert checker.main() == 0


def test_check_no_markers_reports_marker(tmp_path, monkeypatch, capsys, load_script):
    checker = load_script("scripts/check_no_markers.py")
    marker = checker.MARKERS[0]
    (tmp_path / "README.md").write_text(f"bad {marker}\n", encoding="utf-8")
    monkeypatch.setattr(checker, "ROOT", tmp_path)

    assert checker.main() == 1
    assert marker in capsys.readouterr().out


def test_script_test_mapping_is_complete(load_script):
    checker = load_script("scripts/check_script_tests.py")

    assert checker.validate_mapping() == []
    assert len(checker.load_mapping()) == 28
