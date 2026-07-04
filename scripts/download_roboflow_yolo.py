"""Download a Roboflow dataset in YOLOv8 format.

The API key is read from the ROBOFLOW_API_KEY environment variable.
Downloaded files are copied into the requested output directory.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from roboflow import Roboflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--version", required=True, type=int)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def copy_dataset(download_location: Path, output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(download_location, output_dir)


def main() -> None:
    args = parse_args()
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        raise SystemExit("ROBOFLOW_API_KEY environment variable is required")

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(args.workspace).project(args.project)
    version = project.version(args.version)
    dataset = version.download("yolov8")

    download_location = Path(dataset.location)
    output_dir = Path(args.output_dir)
    copy_dataset(download_location, output_dir)

    print(f"Downloaded: {download_location}")
    print(f"Copied to:   {output_dir}")


if __name__ == "__main__":
    main()

