"""Export a trained YOLO model to ONNX."""

from __future__ import annotations

import argparse

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to best.pt")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--opset", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = YOLO(args.model)
    export_kwargs = {
        "format": "onnx",
        "imgsz": args.imgsz,
    }
    if args.opset is not None:
        export_kwargs["opset"] = args.opset

    model.export(**export_kwargs)


if __name__ == "__main__":
    main()

