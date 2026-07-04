"""Merge YOLO datasets while remapping class IDs.

Example:
    python scripts/merge_yolo_datasets.py \
      --source data/processed/openimages_person_box_yolo \
      --target data/processed/dataset_final \
      --class-map 0:0,1:1 \
      --prefix person_box
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_class_map(value: str) -> dict[int, int]:
    result = {}
    for pair in value.split(","):
        src, dst = pair.split(":")
        result[int(src)] = int(dst)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Source YOLO dataset root")
    parser.add_argument("--target", required=True, help="Target YOLO dataset root")
    parser.add_argument("--class-map", required=True, help="Class remap, e.g. 0:2,1:3")
    parser.add_argument("--prefix", required=True, help="Filename prefix for copied files")
    parser.add_argument("--splits", default="train,val", help="Comma-separated splits")
    return parser.parse_args()


def remap_label(src_label: Path, dst_label: Path, class_map: dict[int, int]) -> int:
    kept = 0
    lines = []

    if not src_label.exists():
        return kept

    for line in src_label.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        parts = line.split()
        src_class = int(parts[0])
        if src_class not in class_map:
            continue

        parts[0] = str(class_map[src_class])
        lines.append(" ".join(parts))
        kept += 1

    if kept:
        dst_label.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return kept


def merge_split(source: Path, target: Path, split: str, class_map: dict[int, int], prefix: str) -> tuple[int, int]:
    source_images = source / "images" / split
    source_labels = source / "labels" / split
    target_images = target / "images" / split
    target_labels = target / "labels" / split
    target_images.mkdir(parents=True, exist_ok=True)
    target_labels.mkdir(parents=True, exist_ok=True)

    image_count = 0
    object_count = 0

    for index, image_path in enumerate(sorted(source_images.iterdir())):
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        dst_stem = f"{prefix}_{split}_{index:05d}"
        dst_image = target_images / f"{dst_stem}{image_path.suffix.lower()}"
        dst_label = target_labels / f"{dst_stem}.txt"
        src_label = source_labels / f"{image_path.stem}.txt"

        kept = remap_label(src_label, dst_label, class_map)
        if not kept:
            continue

        shutil.copy2(image_path, dst_image)
        image_count += 1
        object_count += kept

    return image_count, object_count


def write_data_yaml(target: Path) -> None:
    content = """path: .
train: images/train
val: images/val

names:
  0: person
  1: box
  2: traffic_cone
  3: forklift
"""
    (target / "data.yaml").write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    target = Path(args.target)
    class_map = parse_class_map(args.class_map)
    splits = [split.strip() for split in args.splits.split(",") if split.strip()]

    for split in splits:
        images, objects = merge_split(source, target, split, class_map, args.prefix)
        print(f"{split}: copied images={images}, objects={objects}")

    write_data_yaml(target)
    print(f"Wrote merged dataset: {target}")


if __name__ == "__main__":
    main()

