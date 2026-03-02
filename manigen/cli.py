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
        help="One or more dataset directories to scan.",
    )
    parser.add_argument("-o", "--output-file", type=Path, required=True, help="Output file path (e.g., manifest.txt).")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan subdirectories recursively.")
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Number of threads. Use 1 for strict sequential order (default: 1).",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        default=["png", "jpeg", "jpg", "webp", "bmp"],
        help="Allowed file extensions (default: png jpeg jpg webp bmp).",
    )
    parser.add_argument(
        "--strip-prefix",
        type=Path,
        default=None,
        help="Prefix to strip from absolute paths for relative outputs.",
    )
    parser.add_argument("--shuffle", action="store_true", help="Shuffle paths randomly before saving.")
    parser.add_argument(
        "--split",
        type=float,
        nargs="+",
        help="Dataset split ratios, must sum to 1.0 (e.g., 0.8 0.2).",
    )

    args = parser.parse_args()

    if args.threads < 1:
        parser.error(f"Thread count must be >= 1. Got: {args.threads}.")

    if not args.output_file.parent.exists():
        parser.error(f"Output directory does not exist: '{args.output_file.parent}'.")

    if args.split:
        if any(s <= 0 or s >= 1 for s in args.split):
            parser.error("Split ratios must be strictly between 0.0 and 1.0.")

        if abs(sum(args.split) - 1.0) > 1e-5:
            parser.error(f"Split ratios must sum to 1.0. Got: {sum(args.split):.3f}.")

    generate_manifest(
        input_dirs=args.input_dir,
        output_file=args.output_file,
        recursive=args.recursive,
        threads=args.threads,
        extensions=args.extensions,
        strip_prefix=args.strip_prefix,
        shuffle=args.shuffle,
        split_ratios=args.split,
    )


if __name__ == "__main__":
    main()
