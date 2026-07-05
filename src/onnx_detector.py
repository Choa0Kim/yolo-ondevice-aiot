"""YOLOv8 ONNX Runtime detector utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


CLASS_NAMES = ["person", "box", "traffic_cone", "forklift"]


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]

    def to_dict(self) -> dict:
        return {
            "class": self.class_name,
            "confidence": round(self.confidence, 4),
            "bbox": list(self.bbox),
        }


def letterbox(image: np.ndarray, size: int) -> tuple[np.ndarray, float, tuple[float, float]]:
    height, width = image.shape[:2]
    ratio = min(size / width, size / height)
    new_width = int(round(width * ratio))
    new_height = int(round(height * ratio))

    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    pad_x = (size - new_width) / 2
    pad_y = (size - new_height) / 2
    left = int(round(pad_x - 0.1))
    top = int(round(pad_y - 0.1))
    canvas[top : top + new_height, left : left + new_width] = resized
    return canvas, ratio, (left, top)


class YOLOv8ONNXDetector:
    def __init__(
        self,
        model_path: str | Path,
        imgsz: int = 640,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        providers: list[str] | None = None,
    ) -> None:
        self.model_path = str(model_path)
        self.imgsz = imgsz
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.session = ort.InferenceSession(
            self.model_path,
            providers=providers or ["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name

    def detect(self, image: np.ndarray) -> list[Detection]:
        original_height, original_width = image.shape[:2]
        padded, ratio, (pad_x, pad_y) = letterbox(image, self.imgsz)

        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        tensor = rgb.astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))[None, ...]

        outputs = self.session.run(None, {self.input_name: tensor})
        predictions = self._normalize_output(outputs[0])
        return self._postprocess(
            predictions,
            ratio=ratio,
            pad_x=pad_x,
            pad_y=pad_y,
            original_width=original_width,
            original_height=original_height,
        )

    def _normalize_output(self, output: np.ndarray) -> np.ndarray:
        output = np.squeeze(output)
        if output.ndim != 2:
            raise ValueError(f"Unsupported ONNX output shape: {output.shape}")

        # YOLOv8 export usually returns (4 + num_classes, anchors).
        if output.shape[0] < output.shape[1]:
            output = output.T

        return output

    def _postprocess(
        self,
        predictions: np.ndarray,
        ratio: float,
        pad_x: float,
        pad_y: float,
        original_width: int,
        original_height: int,
    ) -> list[Detection]:
        boxes = []
        scores = []
        class_ids = []
        num_classes = len(CLASS_NAMES)

        for row in predictions:
            if row.shape[0] == 4 + num_classes:
                class_scores = row[4:]
            elif row.shape[0] >= 5 + num_classes:
                class_scores = row[5 : 5 + num_classes] * row[4]
            else:
                continue

            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])
            if confidence < self.conf_threshold:
                continue

            cx, cy, width, height = row[:4]
            x1 = (cx - width / 2 - pad_x) / ratio
            y1 = (cy - height / 2 - pad_y) / ratio
            x2 = (cx + width / 2 - pad_x) / ratio
            y2 = (cy + height / 2 - pad_y) / ratio

            x1 = int(np.clip(x1, 0, original_width - 1))
            y1 = int(np.clip(y1, 0, original_height - 1))
            x2 = int(np.clip(x2, 0, original_width - 1))
            y2 = int(np.clip(y2, 0, original_height - 1))
            if x2 <= x1 or y2 <= y1:
                continue

            boxes.append([x1, y1, x2 - x1, y2 - y1])
            scores.append(confidence)
            class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, scores, self.conf_threshold, self.iou_threshold)
        if len(indices) == 0:
            return []

        detections = []
        for index in np.array(indices).flatten():
            x, y, w, h = boxes[index]
            class_id = class_ids[index]
            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=CLASS_NAMES[class_id],
                    confidence=scores[index],
                    bbox=(x, y, x + w, y + h),
                )
            )

        return detections


def draw_detections(image: np.ndarray, detections: list[Detection], risk_level: str | None = None) -> np.ndarray:
    colors = {
        "person": (0, 255, 255),
        "box": (255, 180, 0),
        "traffic_cone": (0, 140, 255),
        "forklift": (0, 0, 255),
    }
    output = image.copy()

    for det in detections:
        x1, y1, x2, y2 = det.bbox
        color = colors.get(det.class_name, (255, 255, 255))
        label = f"{det.class_name} {det.confidence:.2f}"
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        cv2.putText(output, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    if risk_level:
        risk_colors = {"GO": (0, 180, 0), "SLOW": (0, 220, 255), "STOP": (0, 0, 255)}
        color = risk_colors.get(risk_level, (255, 255, 255))
        cv2.putText(output, f"RISK: {risk_level}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)

    return output

