"""Tests for AutoOrganize."""

import tempfile
from pathlib import Path

from autoorganize.rules import OrganizeConfig, match_file
from autoorganize.organizer import plan_moves, execute_moves, undo_last


def _create_messy_dir(tmp: Path) -> None:
    (tmp / "photo.jpg").write_text("image data")
    (tmp / "report.pdf").write_text("pdf data")
    (tmp / "song.mp3").write_text("audio data")
    (tmp / "script.py").write_text("print('hello')")
    (tmp / "data.json").write_text('{"key": "value"}')
    (tmp / "notes.txt").write_text("some notes")
    (tmp / "archive.zip").write_bytes(b"PK\x03\x04")


def test_match_file_default_rules():
    config = OrganizeConfig.default()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        f = root / "photo.jpg"
        f.write_text("data")
        assert match_file(f, config) == "Images"

        f = root / "report.pdf"
        f.write_text("data")
        assert match_file(f, config) == "Documents"

        f = root / "script.py"
        f.write_text("data")
        assert match_file(f, config) == "Code"


def test_match_file_ignores_dotfiles():
    config = OrganizeConfig.default()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        f = root / ".hidden.jpg"
        f.write_text("data")
        assert match_file(f, config) is None


def test_plan_moves():
    config = OrganizeConfig.default()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_messy_dir(root)
        actions = plan_moves(root, config)
        assert len(actions) == 7
        folders = {a.folder for a in actions}
        assert "Images" in folders
        assert "Documents" in folders
        assert "Audio" in folders


def test_execute_and_undo():
    config = OrganizeConfig.default()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_messy_dir(root)

        actions = plan_moves(root, config)
        result = execute_moves(root, actions)

        assert len(result.moved) == 7
        assert (root / "Images" / "photo.jpg").exists()
        assert (root / "Documents" / "report.pdf").exists()
        assert not (root / "photo.jpg").exists()

        undo_result = undo_last(root)
        assert len(undo_result.moved) == 7
        assert (root / "photo.jpg").exists()
        assert not (root / "Images" / "photo.jpg").exists()


def test_duplicate_handling():
    config = OrganizeConfig.default()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "photo.jpg").write_text("first")
        images_dir = root / "Images"
        images_dir.mkdir()
        (images_dir / "photo.jpg").write_text("existing")

        actions = plan_moves(root, config)
        result = execute_moves(root, actions)

        assert len(result.moved) == 1
        assert (root / "Images" / "photo_1.jpg").exists()


def test_unknown_extension_skipped():
    config = OrganizeConfig.default()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "mystery.xyz123").write_text("unknown")
        actions = plan_moves(root, config)
        assert len(actions) == 0
