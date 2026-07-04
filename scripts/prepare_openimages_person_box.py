"""Prepare a small YOLO dataset for Box/Person from Open Images V7.

This script downloads a limited Open Images subset with FiftyOne, keeps only
Box and Person detections, samples a small balanced subset, and writes YOLO
labels in the project class order:

0: person
1: box
2: traffic_cone
3: forklift
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
from collections import Counter
from pathlib import Path

# Keep downloaded source data inside the project workspace.
os.environ.setdefault(
    "FIFTYONE_DATASET_ZOO_DIR",
    str(Path("data/external/fiftyone").resolve()),
)

import fiftyone.zoo as foz
from fiftyone import ViewField as F


OPEN_IMAGES_CLASSES = ["Box", "Person"]
PROJECT_CLASS_IDS = {
    "Person": 0,
    "Box": 1,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-samples", type=int, default=300)
    parser.add_argument("--train-per-class", type=int, default=64)
    parser.add_argument("--val-per-class", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        default="data/processed/openimages_person_box_yolo",
        help="Output YOLO dataset directory",
    )
    parser.add_argument(
        "--dataset-name",
        default="local_openimages_person_box_source",
        help="FiftyOne dataset name",
    )
    return parser.parse_args()


def filtered_source(dataset_name: str, source_samples: int, seed: int):
    dataset = foz.load_zoo_dataset(
        "open-images-v7",
        split="train",
        label_types=["detections"],
        classes=OPEN_IMAGES_CLASSES,
        max_samples=source_samples,
        shuffle=True,
        seed=seed,
        only_matching=True,
        dataset_name=dataset_name,
        overwrite=True,
    )

    return dataset.filter_labels(
        "ground_truth",
        F("label").is_in(OPEN_IMAGES_CLASSES),
        only_matches=True,
    )


def sample_records(view, per_class_targets: dict[str, int], seed: int, excluded: set[str]):
    records = []
    class_image_counts = Counter()
    rng = random.Random(seed)
    samples = list(view)
    rng.shuffle(samples)

    for sample in samples:
        if sample.id in excluded:
            continue

        labels = {
            det.label
            for det in sample.ground_truth.detections
            if det.label in per_class_targets
        }
        if not labels:
            continue

        helps = any(class_image_counts[label] < per_class_targets[label] for label in labels)
        if not helps:
            continue

        records.append(sample)
        excluded.add(sample.id)
        for label in labels:
            if class_image_counts[label] < per_class_targets[label]:
                class_image_counts[label] += 1

        if all(class_image_counts[label] >= target for label, target in per_class_targets.items()):
            break

    return records, class_image_counts


def write_split(records, split: str, output_dir: Path) -> Counter:
    image_out = output_dir / "images" / split
    label_out = output_dir / "labels" / split
    image_out.mkdir(parents=True, exist_ok=True)
    label_out.mkdir(parents=True, exist_ok=True)

    object_counts = Counter()

    for idx, sample in enumerate(records):
        src = Path(sample.filepath)
        suffix = src.suffix.lower() or ".jpg"
        stem = f"{split}_{idx:05d}"
        dst_image = image_out / f"{stem}{suffix}"
        dst_label = label_out / f"{stem}.txt"

        shutil.copy2(src, dst_image)

        lines = []
        for det in sample.ground_truth.detections:
            if det.label not in PROJECT_CLASS_IDS:
                continue

            x, y, w, h = det.bounding_box
            x_center = x + w / 2
            y_center = y + h / 2
            class_id = PROJECT_CLASS_IDS[det.label]
            lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
            object_counts[det.label] += 1

        dst_label.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return object_counts


def write_data_yaml(output_dir: Path) -> None:
    content = """path: .
train: images/train
val: images/val

names:
  0: person
  1: box
  2: traffic_cone
  3: forklift
"""
    (output_dir / "data.yaml").write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)

    view = filtered_source(args.dataset_name, args.source_samples, args.seed)
    print(f"Filtered source samples: {len(view)}")

    excluded: set[str] = set()
    val_targets = {label: args.val_per_class for label in OPEN_IMAGES_CLASSES}
    train_targets = {label: args.train_per_class for label in OPEN_IMAGES_CLASSES}

    val_records, val_image_counts = sample_records(view, val_targets, args.seed, excluded)
    train_records, train_image_counts = sample_records(view, train_targets, args.seed + 1, excluded)

    train_object_counts = write_split(train_records, "train", output_dir)
    val_object_counts = write_split(val_records, "val", output_dir)
    write_data_yaml(output_dir)

    print("Image counts")
    print("  train:", dict(train_image_counts), "samples:", len(train_records))
    print("  val:  ", dict(val_image_counts), "samples:", len(val_records))
    print("Object counts")
    print("  train:", dict(train_object_counts))
    print("  val:  ", dict(val_object_counts))
    print(f"Wrote: {output_dir}")


if __name__ == "__main__":
    main()
