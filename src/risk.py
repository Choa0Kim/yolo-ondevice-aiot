"""Rule-based risk scoring for AMR safety monitoring."""

from __future__ import annotations

from onnx_detector import Detection


def calculate_risk(detections: list[Detection], frame_width: int, frame_height: int) -> tuple[str, str]:
    risk = "GO"
    reason = "no risky object detected"

    for det in detections:
        x1, _y1, x2, y2 = det.bbox
        center_x = (x1 + x2) / 2
        bottom_y = y2

        in_center_lane = frame_width * 0.30 <= center_x <= frame_width * 0.70
        in_warning_zone = bottom_y >= frame_height * 0.45
        in_stop_zone = bottom_y >= frame_height * 0.65

        if not in_warning_zone:
            continue

        if det.class_name in {"person", "forklift"} and in_center_lane and in_stop_zone:
            return "STOP", f"{det.class_name} detected in center lane stop zone"

        if det.class_name in {"box", "traffic_cone"} and in_center_lane and in_stop_zone:
            return "STOP", f"{det.class_name} detected in center lane stop zone"

        if det.class_name in {"person", "forklift", "box", "traffic_cone"}:
            risk = "SLOW"
            reason = f"{det.class_name} detected in warning zone"

    return risk, reason
