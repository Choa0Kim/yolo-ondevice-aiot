"""Normalize a Roboflow YOLOv8 export to this project's YOLO layout.

Roboflow commonly exports:
  train/images, train/labels, valid/images, valid/labels, test/...

This script writes:
  images/train, labels/train, images/val, labels/val

It can also keep only selected source class IDs and remap them to project class
IDs.
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
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--class-map", required=True)
    parser.add_argument("--prefix", required=True)
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


def copy_split(source: Path, target: Path, source_split: str, target_split: str, class_map: dict[int, int], prefix: str):
    src_images = source / source_split / "images"
    src_labels = source / source_split / "labels"
    dst_images = target / "images" / target_split
    dst_labels = target / "labels" / target_split
    dst_images.mkdir(parents=True, exist_ok=True)
    dst_labels.mkdir(parents=True, exist_ok=True)

    image_count = 0
    object_count = 0

    if not src_images.exists():
        return image_count, object_count

    for index, image_path in enumerate(sorted(src_images.iterdir())):
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        dst_stem = f"{prefix}_{target_split}_{index:05d}"
        src_label = src_labels / f"{image_path.stem}.txt"
        dst_label = dst_labels / f"{dst_stem}.txt"
        kept = remap_label(src_label, dst_label, class_map)
        if not kept:
            continue

        shutil.copy2(image_path, dst_images / f"{dst_stem}{image_path.suffix.lower()}")
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

    if target.exists():
        shutil.rmtree(target)

    train_images, train_objects = copy_split(source, target, "train", "train", class_map, args.prefix)
    val_images, val_objects = copy_split(source, target, "valid", "val", class_map, args.prefix)
    write_data_yaml(target)

    print(f"train: images={train_images}, objects={train_objects}")
    print(f"val: images={val_images}, objects={val_objects}")
    print(f"Wrote: {target}")


if __name__ == "__main__":
    main()

