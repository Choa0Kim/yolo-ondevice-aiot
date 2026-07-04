"""Check YOLO dataset image/label counts and class distribution."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir")
    return parser.parse_args()


def count_split(dataset_dir: Path, split: str) -> tuple[int, int, Counter]:
    image_dir = dataset_dir / "images" / split
    label_dir = dataset_dir / "labels" / split
    images = [p for p in image_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    labels = list(label_dir.glob("*.txt"))
    counts = Counter()

    for label_file in labels:
        for line in label_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            counts[int(line.split()[0])] += 1

    return len(images), len(labels), counts


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.dataset_dir)

    for split in ["train", "val"]:
        image_count, label_count, class_counts = count_split(dataset_dir, split)
        print(f"{split}: images={image_count}, labels={label_count}, classes={dict(class_counts)}")

    data_yaml = dataset_dir / "data.yaml"
    if data_yaml.exists():
        print("\ndata.yaml")
        print(data_yaml.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

