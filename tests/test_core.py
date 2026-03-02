import threading
from pathlib import Path

from manigen.core import format_extensions, format_path, generate_manifest, process_and_save, scan_worker


def test_format_extension() -> None:
    extensions = ["png", ".jpg", "WeBp"]
    formatted_extension = format_extensions(extensions=extensions)
    assert formatted_extension == {".png", ".jpg", ".webp"}


def test_format_path_absolute(tmp_path: Path) -> None:
    file_path = tmp_path / "image.png"
    formatted_path = format_path(path=file_path, strip_prefix=None)
    assert Path(formatted_path) == file_path.absolute()


def test_format_path_relative(tmp_path: Path) -> None:
    base_dir = tmp_path / "dataset"
    file_path = base_dir / "train" / "image.png"
    formatted_path = format_path(path=file_path, strip_prefix=base_dir)
    assert Path(formatted_path) == Path("train/image.png")


def test_format_path_wrong_strip_prefix(tmp_path: Path) -> None:
    base_dir = tmp_path / "dataset"
    file_path = base_dir / "train" / "image.png"
    formatted_path = format_path(path=file_path, strip_prefix=(tmp_path / "files"))
    assert Path(formatted_path) == file_path.absolute()


def test_scan_worker_without_recursion(tmp_path: Path) -> None:
    (tmp_path / "image.png").touch()
    (tmp_path / "file.txt").touch()

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / "nested_image.jpg").touch()

    formatted_paths = []
    list_lock = threading.Lock()
    extensions = {".png", ".jpg"}

    scan_worker(
        directory=tmp_path,
        recursive=False,
        formatted_paths=formatted_paths,
        list_lock=list_lock,
        extensions=extensions,
        strip_prefix=None,
    )

    assert len(formatted_paths) == 1
    assert "image.png" in formatted_paths[0]


def test_scan_worker_with_recursion(tmp_path: Path) -> None:
    (tmp_path / "image.png").touch()
    (tmp_path / "file.txt").touch()

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / "nested_image.jpg").touch()

    formatted_paths = []
    list_lock = threading.Lock()
    extensions = {".png", ".jpg"}

    scan_worker(
        directory=tmp_path,
        recursive=True,
        formatted_paths=formatted_paths,
        list_lock=list_lock,
        extensions=extensions,
        strip_prefix=None,
    )

    assert len(formatted_paths) == 2
    assert any("nested_image.jpg" in path for path in formatted_paths)


def test_process_and_save(tmp_path: Path) -> None:
    fake_paths = [f"dataset/image_{i}.png" for i in range(100)]
    output_file = tmp_path / "manifest.txt"

    process_and_save(
        formatted_paths=fake_paths.copy(),
        output_file=output_file,
        shuffle=True,
        split_ratios=[0.7, 0.2, 0.1],
    )

    train_file = tmp_path / "manifest_train.txt"
    val_file = tmp_path / "manifest_val.txt"
    test_file = tmp_path / "manifest_test.txt"

    assert train_file.exists()
    assert val_file.exists()
    assert test_file.exists()

    assert len(train_file.read_text().splitlines()) == 70
    assert len(val_file.read_text().splitlines()) == 20
    assert len(test_file.read_text().splitlines()) == 10


def test_generate_manifest_sequential(tmp_path: Path) -> None:
    (tmp_path / "image.png").touch()

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / "nested_image.jpg").touch()

    output_file = tmp_path / "manifest.txt"

    generate_manifest(
        input_dirs=[tmp_path],
        output_file=output_file,
        recursive=True,
        threads=1,
    )

    assert len(output_file.read_text(encoding="utf-8").splitlines()) == 2


def test_generate_manifest_parallel(tmp_path: Path) -> None:
    (tmp_path / "image.png").touch()

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / "nested_image.jpg").touch()

    output_file = tmp_path / "manifest.txt"

    generate_manifest(
        input_dirs=[tmp_path],
        output_file=output_file,
        recursive=True,
        threads=4,
    )

    assert len(output_file.read_text(encoding="utf-8").splitlines()) == 2
