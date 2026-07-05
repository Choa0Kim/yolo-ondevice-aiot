"""Run ONNX object detection on an image, video, or webcam source.

Optionally publishes detection events to MQTT.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover
    mqtt = None

from onnx_detector import YOLOv8ONNXDetector, draw_detections
from risk import calculate_risk


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/best.onnx")
    parser.add_argument("--source", required=True, help="Image path, video path, or webcam index")
    parser.add_argument("--output", default="output/detections")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--device-id", default="edge-camera-01")
    parser.add_argument("--mqtt-host", default=None)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-topic", default="aiot/detection")
    parser.add_argument("--show", action="store_true")
    return parser.parse_args()


def mqtt_client(host: str | None, port: int):
    if not host:
        return None
    if mqtt is None:
        raise RuntimeError("paho-mqtt is not installed")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(host, port, keepalive=60)
    client.loop_start()
    return client


def publish(client, topic: str, payload: dict) -> None:
    if client is not None:
        client.publish(topic, json.dumps(payload, ensure_ascii=False))


def event_payload(device_id: str, detections, risk_level: str, reason: str, fps: float) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": device_id,
        "domain": "smart_factory_logistics",
        "objects": [det.to_dict() for det in detections],
        "risk_level": risk_level,
        "reason": reason,
        "fps": round(fps, 2),
    }


def run_image(args: argparse.Namespace, detector: YOLOv8ONNXDetector, client) -> None:
    image = cv2.imread(args.source)
    if image is None:
        raise FileNotFoundError(args.source)

    start = time.perf_counter()
    detections = detector.detect(image)
    fps = 1.0 / max(time.perf_counter() - start, 1e-9)
    risk_level, reason = calculate_risk(detections, image.shape[1], image.shape[0])
    output = draw_detections(image, detections, risk_level)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{Path(args.source).stem}_detected.jpg"
    cv2.imwrite(str(output_path), output)

    payload = event_payload(args.device_id, detections, risk_level, reason, fps)
    publish(client, args.mqtt_topic, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Wrote: {output_path}")


def run_video(args: argparse.Namespace, detector: YOLOv8ONNXDetector, client) -> None:
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {args.source}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    input_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "result_video.mp4"
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        input_fps,
        (width, height),
    )

    frame_index = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            start = time.perf_counter()
            detections = detector.detect(frame)
            elapsed = time.perf_counter() - start
            fps = 1.0 / max(elapsed, 1e-9)
            risk_level, reason = calculate_risk(detections, width, height)
            annotated = draw_detections(frame, detections, risk_level)
            cv2.putText(annotated, f"FPS: {fps:.1f}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            writer.write(annotated)

            payload = event_payload(args.device_id, detections, risk_level, reason, fps)
            payload["frame_index"] = frame_index
            publish(client, args.mqtt_topic, payload)

            if frame_index % 30 == 0:
                print(json.dumps(payload, ensure_ascii=False))

            if args.show:
                cv2.imshow("ONNX Detection", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_index += 1
    finally:
        cap.release()
        writer.release()
        if args.show:
            cv2.destroyAllWindows()

    print(f"Wrote: {output_path}")


def main() -> None:
    args = parse_args()
    detector = YOLOv8ONNXDetector(
        args.model,
        imgsz=args.imgsz,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
    )
    client = mqtt_client(args.mqtt_host, args.mqtt_port)

    source_path = Path(args.source)
    try:
        if source_path.suffix.lower() in IMAGE_SUFFIXES:
            run_image(args, detector, client)
        else:
            run_video(args, detector, client)
    finally:
        if client is not None:
            client.loop_stop()
            client.disconnect()


if __name__ == "__main__":
    main()
