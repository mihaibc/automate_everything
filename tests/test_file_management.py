import pytest


def test_move_files_dry_run_does_not_move(tmp_path, load_script):
    move_files = load_script("Python/file_management/move_files.py")
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    keep = source / "notes.txt"
    match = source / "paper.pdf"
    keep.write_text("keep", encoding="utf-8")
    match.write_text("move", encoding="utf-8")

    results = move_files.move_files(source, destination, ["pdf"], dry_run=True)

    assert len(results) == 1
    assert results[0].source == match
    assert results[0].destination == destination / "paper.pdf"
    assert match.exists()
    assert not destination.exists()


def test_move_files_renames_collisions(tmp_path, load_script):
    move_files = load_script("Python/file_management/move_files.py")
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "report.pdf").write_text("new", encoding="utf-8")
    (destination / "report.pdf").write_text("existing", encoding="utf-8")

    results = move_files.move_files(source, destination, [".pdf"], collision="rename")

    assert len(results) == 1
    assert results[0].action == "renamed"
    assert (destination / "report.pdf").read_text(encoding="utf-8") == "existing"
    assert (destination / "report-1.pdf").read_text(encoding="utf-8") == "new"


def test_move_files_validates_inputs(tmp_path, load_script):
    move_files = load_script("Python/file_management/move_files.py")

    with pytest.raises(ValueError, match="extension"):
        move_files.move_files(tmp_path, tmp_path / "dest", [""])

    with pytest.raises(NotADirectoryError):
        move_files.move_files(tmp_path / "missing", tmp_path / "dest", ["txt"])


def test_create_folder_structure_supports_dry_run(tmp_path, load_script):
    create_folder = load_script("Python/file_management/create_folder_structure.py")
    structure = {"Python": ["local_ai"], "Bash": ["local_ai"]}

    paths = create_folder.create_folder_structure(tmp_path, structure, dry_run=True)

    assert paths == [tmp_path / "Python" / "local_ai", tmp_path / "Bash" / "local_ai"]
    assert not (tmp_path / "Python").exists()


def test_create_folder_structure_creates_paths(tmp_path, load_script):
    create_folder = load_script("Python/file_management/create_folder_structure.py")
    structure = {"Python": ["local_ai"]}

    paths = create_folder.create_folder_structure(tmp_path, structure)

    assert paths == [tmp_path / "Python" / "local_ai"]
    assert (tmp_path / "Python" / "local_ai").is_dir()
