from concurrent.futures import ThreadPoolExecutor
import random
from pathlib import Path
import threading


def format_extensions(extensions: list[str]) -> set[str]:
    return {f".{extension.lstrip('.').lower()}" for extension in extensions}


def format_path(path: Path, strip_prefix: Path | None) -> str:
    if strip_prefix:
        try:
            return str(path.resolve().relative_to(strip_prefix.resolve()))
        except ValueError:
            pass

    return str(path.absolute())


def scan_worker(
    directory: Path,
    recursive: bool,
    formatted_paths: list[str],
    list_lock: threading.Lock,
    extensions: set[str],
    strip_prefix: Path | None,
) -> None:
    try:
        paths = directory.rglob("*") if recursive else directory.glob("*")
        for path in paths:
            if path.is_file() and path.suffix.lower() in extensions:
                formatted_path = format_path(path=path, strip_prefix=strip_prefix)
                with list_lock:
                    formatted_paths.append(formatted_path)
    except Exception as e:
        print(f"Error scanning directory '{directory}': {e}")


def process_and_save(
    formatted_paths: list[str],
    output_file: Path,
    shuffle: bool,
    split_ratios: list[float] | None,
) -> None:
    if not formatted_paths:
        print("No valid files found! Manifest was not created.")
        return

    if shuffle:
        print("Shuffling paths...")
        random.shuffle(formatted_paths)

    if split_ratios:
        split_suffixes = ["_train", "_val", "_test"]
        num_paths = len(formatted_paths)
        start = 0

        for i, ratio in enumerate(split_ratios):
            if i == len(split_ratios) - 1:
                end = num_paths
            else:
                end = start + int(num_paths * ratio)

            split_suffix = split_suffixes[i] if i < len(split_suffixes) else f"_split_{i}"
            split_file = output_file.with_name(f"{output_file.stem}{split_suffix}{output_file.suffix}")

            with open(split_file, "w", encoding="utf-8") as f:
                f.write("\n".join(formatted_paths[start:end]) + "\n")

            print(f"Saved {end - start} paths to {split_file.name}")
            start = end
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(formatted_paths) + "\n")
        print(f"Done! Saved {len(formatted_paths)} paths to {output_file.name}")


def generate_manifest(
    input_dirs: list[Path],
    output_file: Path,
    recursive: bool = True,
    threads: int = 1,
    extensions: list[str] = ["png", "jpeg", "jpg", "webp", "bmp"],
    strip_prefix: Path | None = None,
    shuffle: bool = False,
    split_ratios: list[float] | None = None,
) -> None:
    extensions_set = format_extensions(extensions)
    formatted_paths = []
    list_lock = threading.Lock()

    if threads == 1:
        print("Running in sequential mode...")
        for directory in input_dirs:
            if not directory.exists():
                print(f"Warning: directory '{directory}' not found. Skipping...")
                continue

            scan_worker(
                directory=directory,
                recursive=recursive,
                formatted_paths=formatted_paths,
                list_lock=list_lock,
                extensions=extensions_set,
                strip_prefix=strip_prefix,
            )
    else:
        print(f"Running in parallel mode with {threads} threads...")

        tasks = []
        for directory in input_dirs:
            if not directory.exists():
                print(f"Warning: directory '{directory}' not found. Skipping...")
                continue

            if recursive:
                tasks.append((directory, False))
                for path in directory.iterdir():
                    if path.is_dir():
                        tasks.append((path, True))
            else:
                tasks.append((directory, False))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for task_dir, is_recursive in tasks:
                executor.submit(
                    scan_worker,
                    task_dir,
                    is_recursive,
                    formatted_paths,
                    list_lock,
                    extensions_set,
                    strip_prefix,
                )

    process_and_save(
        formatted_paths=formatted_paths,
        output_file=output_file,
        shuffle=shuffle,
        split_ratios=split_ratios,
    )
