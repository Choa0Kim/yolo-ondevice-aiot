"""Create a short MP4 video from validation images for pipeline testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--output", default="output/input/validation_slideshow.mp4")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--size", type=int, default=640)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(
        p for p in source_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )[: args.limit]
    if not image_paths:
        raise SystemExit(f"No images found in {source_dir}")

    frame_size = (args.size, args.size)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        args.fps,
        frame_size,
    )

    for image_path in image_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            continue
        image = cv2.resize(image, frame_size)
        for _ in range(args.repeat):
            writer.write(image)

    writer.release()
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()

