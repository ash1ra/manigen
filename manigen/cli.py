import argparse
from pathlib import Path

from .core import generate_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="manigen — fast and reliable dataset manifest generator.")

    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        nargs="+",
        required=True,
        help="Paths to one or more dataset directories",
    )
    parser.add_argument("-o", "--output-file", type=Path, required=True, help="Path to output file")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search recursively")
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Number of threads (default: 1 for sequential order)",
    )
    parser.add_argument(
        "-e",
        "--ext",
        nargs="+",
        default=["png", "jpeg", "jpg", "webp", "bmp"],
        help="File extensions to include (default: png jpeg jpg webp bmp)",
    )
    parser.add_argument(
        "--strip-prefix",
        type=Path,
        default=None,
        help="Strip part of the absolute path (default: None)",
    )
    parser.add_argument("--shuffle", action="store_true", help="Shuffle the paths before saving")
    parser.add_argument(
        "--split",
        type=float,
        nargs="+",
        help="Split ratios for Train/Val/Test (e.g., 0.8 0.2)",
    )

    args = parser.parse_args()

    if args.split:
        if any(s <= 0 or s >= 1 for s in args.split):
            parser.error("Each split ratio must be greater than 0 and less than 1.")

        if abs(sum(args.split) - 1.0) > 1e-5:
            parser.error(f"Split ratios must sum to 1.0. Current sum: {sum(args.split):.3f}")

    generate_manifest(
        input_dirs=args.input_dir,
        output_file=args.output_file,
        recursive=args.recursive,
        threads=args.threads,
        extensions=args.ext,
        strip_prefix=args.strip_prefix,
        shuffle=args.shuffle,
        split_ratios=args.split,
    )


if __name__ == "__main__":
    main()
