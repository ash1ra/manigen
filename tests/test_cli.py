from pathlib import Path
from unittest.mock import patch

import pytest
from pytest import CaptureFixture

from manigen.cli import main


def test_cli_output_file_dir_not_exists(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    output_file = tmp_path / "fake_dir" / "manifest.txt"

    test_args = ["mangen", "-i", str(tmp_path), "-o", str(output_file)]

    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()
    assert "Output directory does not exist" in captured.err


def test_cli_invalid_threads(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    output_file = tmp_path / "manifest.txt"

    test_args = ["mangen", "-i", str(tmp_path), "-o", str(output_file), "-t", "0"]

    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()
    assert "Thread count must be >= 1" in captured.err


def test_cli_invalid_split(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    output_file = tmp_path / "manifest.txt"

    test_args = ["mangen", "-i", str(tmp_path), "-o", str(output_file), "--split", "0.8", "0.5"]

    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()
    assert "Split ratios must sum to 1.0" in captured.err
