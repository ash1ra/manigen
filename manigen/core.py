from concurrent.futures import ThreadPoolExecutor
import random
from pathlib import Path
import threading


def format_extensions(extensions: list[str]) -> set[str]:
    return {f".{extention.lstrip('.').lower()}" for extention in extensions}


def format_path(item: Path, strip_prefix: Path | None) -> str:
    if strip_prefix:
        try:
            return str(item.resolve().relative_to(strip_prefix.resolve()))
        except ValueError:
            pass

    return str(item.absolute())


def scan_worker(
    directory: Path,
    recursive: bool,
    result_list: list[str],
    list_lock: threading.Lock,
    extensions: set[str],
    strip_prefix: Path | None,
) -> None:
    try:
        items = directory.rglob("*") if recursive else directory.glob("*")
        for item in items:
            if item.is_file() and item.suffix.lower() in extensions:
                item_formatted = format_path(item=item, strip_prefix=strip_prefix)
                with list_lock:
                    result_list.append(item_formatted)
    except Exception as e:
        print(f"Error scanning directory '{directory}': {e}")


def process_and_save(
    all_paths: list[str],
    output_file: Path,
    shuffle: bool,
    split_ratios: list[float] | None,
) -> None:
    if not all_paths:
        print("No valid files found! Manifest was not created.")
        return

    if shuffle:
        print("Shuffling paths...")
        random.shuffle(all_paths)

    if split_ratios:
        suffixes = ["_train", "_val", "_test"]
        total = len(all_paths)
        start = 0

        for i, ratio in enumerate(split_ratios):
            if i == len(split_ratios) - 1:
                end = total
            else:
                end = start + int(total * ratio)

            suffix = suffixes[i] if i < len(suffixes) else f"_split_{i}"
            split_file = output_file.with_name(f"{output_file.stem}{suffix}{output_file.suffix}")

            with open(split_file, "w", encoding="utf-8") as f:
                f.write("\n".join(all_paths[start:end]) + "\n")

            print(f"Saved {end - start} paths to {split_file.name}")
            start = end
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(all_paths) + "\n")
        print(f"Done! Saved {len(all_paths)} paths to {output_file.name}")


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
    allowed_extentions = format_extensions(extensions)
    result_list = []
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
                result_list=result_list,
                list_lock=list_lock,
                extensions=allowed_extentions,
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
                for sub_item in directory.iterdir():
                    if sub_item.is_dir():
                        tasks.append((sub_item, True))
            else:
                tasks.append((directory, False))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for task_dir, is_recursive in tasks:
                executor.submit(
                    scan_worker,
                    task_dir,
                    is_recursive,
                    result_list,
                    list_lock,
                    allowed_extentions,
                    strip_prefix,
                )

    process_and_save(
        all_paths=result_list,
        output_file=output_file,
        shuffle=shuffle,
        split_ratios=split_ratios,
    )
