# manigen 📝

[![PyPI Version](https://img.shields.io/pypi/v/manigen.svg)](https://pypi.org/project/manigen/)
[![Python Versions](https://img.shields.io/pypi/pyversions/manigen.svg)](https://pypi.org/project/manigen/)
[![License](https://img.shields.io/pypi/l/manigen.svg)](https://pypi.org/project/manigen/)
[![CI Status](https://github.com/ash1ra/manigen/actions/workflows/ci.yml/badge.svg)](https://github.com/ash1ra/manigen/actions)

**manigen** is a fast and reliable CLI tool designed to generate file manifests (lists of file paths) for Machine Learning and Deep Learning datasets.

Whether you are preparing a small local dataset or parsing a massive image corpus like ImageNet, `manigen` handles recursive scanning, multithreading, path formatting, and Train/Val/Test splitting out of the box.

## ✨ Features

* ⏱️ **Efficient & Multithreaded**: Uses a thread pool to parallelize I/O operations, significantly speeding up the scanning of large and deeply nested directory trees compared to sequential scripts.
* ✂️ **Portable Manifests**: Generate relative paths by stripping absolute prefixes (`--strip-prefix`), making it easy to move datasets between local machines and cloud servers.
* 🔀 **ML-Ready Splits**: Built-in shuffling and automatic Train/Validation/Test dataset splitting directly into separate files (`--split`).
* 🛡️ **Robust Architecture**: Built with modern Python, featuring thread-safe list operations, strict input validation, and clear error handling.

## 🎯 Motivation

While working on Super-Resolution Deep Learning projects, I found myself repeatedly copying the same massive datasets across multiple project directories. To save disk space, I decided to store all datasets in a single central location (e.g., `~/.local/share/datasets`) and feed the models using simple text files containing absolute paths to the images. 

Initially, I wrote a bash script for this task. However, generating a manifest for the ImageNet dataset took about 30 minutes. By rewriting the tool in Python and leveraging multithreading, `manigen` can now generate a manifest for ImageNet (1,281,167 images) in **12 seconds**.

## 📦 Installation

You can install `manigen` directly from PyPI using `pip`:

```bash
pip install manigen
```

Or, if you use `uv` (recommended for CLI tools):

```bash
uv tool install manigen
```

## 🚀 Quick Start

Generate a manifest of all images in a dataset directory:

```bash
manigen -i ./datasets/ImageNet/train -o manifest.txt
```

## 💡 Advanced Usage Examples

### 1. Multithreaded Scanning

Speed up scanning for datasets with heavily nested directories (like ImageNet) by utilizing multiple threads and recursive search:

```bash
manigen -i ./datasets/ImageNet/train -o train_paths.txt -t 8 -r
```

### 2. Making Paths Portable (Relative Paths)

If your absolute path is `/Users/ml_engineer/projects/data/images/cat.jpg`, but you want the manifest to only contain `data/images/cat.jpg`:

```bash
manigen -i /Users/ml_engineer/projects/data -o dataset.txt --strip-prefix /Users/ml_engineer/projects/
```

### 3. Creating Train/Val/Test Splits

Automatically shuffle the dataset and split it into training (70%), validation (20%), and testing (10%) sets:

```bash
manigen -i ./dataset -o manifest.txt --shuffle --split 0.7 0.2 0.1
```

### 4. Custom File Extensions

Override the default extensions to scan for audio, text, or any other formats:

```bash
manigen -i ./audio_dataset -o audio_manifest.txt -e wav mp3 flac
```

## 🛠️ CLI Reference

| Argument | Short | Description | Default
| --- | :---: | --- | :---:
| `--input-dir` | `-i` | **(Required)** One or more dataset directories to scan. | -
| `--output-file` | `-o` | **(Required)** Output file path (e.g., `manifest.txt`). | -
| `--threads` | `-t` | Number of threads for parallel scanning. | `1`
| `--recursive` | `-r` | Scan subdirectories recursively. | `False`
| `--extensions` | `-e` | Allowed file extensions. | `png jpeg jpg webp bmp`
| `--strip-prefix` |   | Prefix to strip from absolute paths for relative outputs. | `None`
| `--shuffle` |   | Shuffle paths randomly before saving. | `False`
| `--split` |   | Dataset split ratios, must sum to 1.0 (e.g., `0.8 0.2`). | `None`

## 🤝 Contributing

### 1. Clone the repository

```bash
git clone https://github.com/ash1ra/manigen
cd manigen
```

### 2. Install dependencies using uv

```bash
uv sync
# On Windows
.venv\Scripts\activate
# on Unix or MacOS
source .venv/bin/activate
```

### 3. Format and lint the code 

```bash
uv run ruff format .
uv run ruff check .
```

### 4. Run the tests 

```bash
uv run pytest tests/ -v
```

### 5. Submit a pull request

If you'd like to contribute, please fork the repository and open a pull request to the `main` branch.
