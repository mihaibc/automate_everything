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


def test_move_files_skip_overwrite_and_error_collisions(tmp_path, load_script):
    move_files = load_script("Python/file_management/move_files.py")
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()

    (source / "skip.txt").write_text("new", encoding="utf-8")
    (destination / "skip.txt").write_text("existing", encoding="utf-8")
    results = move_files.move_files(source, destination, ["txt"], collision="skip")
    assert results[0].action == "skipped"
    assert (source / "skip.txt").exists()
    assert (destination / "skip.txt").read_text(encoding="utf-8") == "existing"

    (source / "overwrite.txt").write_text("new", encoding="utf-8")
    (destination / "overwrite.txt").write_text("existing", encoding="utf-8")
    results = move_files.move_files(source, destination, ["txt"], collision="overwrite")
    assert results[0].action == "overwritten"
    assert (destination / "overwrite.txt").read_text(encoding="utf-8") == "new"

    (source / "error.txt").write_text("new", encoding="utf-8")
    (destination / "error.txt").write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError):
        move_files.move_files(source, destination, ["txt"], collision="error")


def test_move_files_non_recursive_and_destination_inside_source(tmp_path, load_script):
    move_files = load_script("Python/file_management/move_files.py")
    source = tmp_path / "source"
    nested = source / "nested"
    destination = source / "destination"
    nested.mkdir(parents=True)
    destination.mkdir()
    (source / "top.txt").write_text("top", encoding="utf-8")
    (nested / "nested.txt").write_text("nested", encoding="utf-8")
    (destination / "already.txt").write_text("already", encoding="utf-8")

    results = move_files.move_files(source, destination, ["txt"], recursive=False)

    assert [result.source.name for result in results] == ["top.txt"]
    assert (destination / "top.txt").exists()
    assert (nested / "nested.txt").exists()
    assert (destination / "already.txt").exists()


def test_move_files_validates_inputs(tmp_path, load_script):
    move_files = load_script("Python/file_management/move_files.py")

    with pytest.raises(ValueError, match="extension"):
        move_files.move_files(tmp_path, tmp_path / "dest", [""])

    with pytest.raises(NotADirectoryError):
        move_files.move_files(tmp_path / "missing", tmp_path / "dest", ["txt"])


def test_move_files_cli_reports_errors(tmp_path, capsys, load_script):
    move_files = load_script("Python/file_management/move_files.py")

    exit_code = move_files.main(
        [
            "--source",
            str(tmp_path / "missing"),
            "--destination",
            str(tmp_path / "dest"),
            "--extensions",
            "txt",
        ]
    )

    assert exit_code == 1
    assert "source folder" in capsys.readouterr().err


def test_create_folder_structure_supports_dry_run(tmp_path, load_script):
    create_folder = load_script("Python/file_management/create_folder_structure.py")
    structure = {"Python": ["local_ai"], "Bash": ["local_ai"]}

    paths = create_folder.create_folder_structure(tmp_path, structure, dry_run=True)

    assert paths == [tmp_path / "Python" / "local_ai", tmp_path / "Bash" / "local_ai"]
    assert not (tmp_path / "Python").exists()


def test_create_folder_structure_loads_and_rejects_json(tmp_path, load_script):
    create_folder = load_script("Python/file_management/create_folder_structure.py")
    structure_file = tmp_path / "structure.json"
    structure_file.write_text('{"Docs":["api"]}', encoding="utf-8")

    assert create_folder.load_structure(str(structure_file)) == {"Docs": ["api"]}

    bad_file = tmp_path / "bad.json"
    bad_file.write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        create_folder.load_structure(str(bad_file))

    with pytest.raises(ValueError, match="must map"):
        create_folder.create_folder_structure(tmp_path, {"Bad": "not-list"})


def test_create_folder_structure_creates_paths(tmp_path, load_script):
    create_folder = load_script("Python/file_management/create_folder_structure.py")
    structure = {"Python": ["local_ai"]}

    paths = create_folder.create_folder_structure(tmp_path, structure)

    assert paths == [tmp_path / "Python" / "local_ai"]
    assert (tmp_path / "Python" / "local_ai").is_dir()
