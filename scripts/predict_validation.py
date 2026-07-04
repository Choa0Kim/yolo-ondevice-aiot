"""Run prediction on validation images with a trained YOLO model."""

from __future__ import annotations

import argparse

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to best.pt or best.onnx")
    parser.add_argument("--source", required=True, help="Validation image directory")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--project", default="runs")
    parser.add_argument("--name", default="val_predictions")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = YOLO(args.model)
    model.predict(
        source=args.source,
        imgsz=args.imgsz,
        conf=args.conf,
        save=True,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()

