# Source Code

로컬 실행 코드를 보관합니다.

예상 파일:

```text
onnx_inference.py
onnx_inference_mqtt.py
onnx_detector.py
risk.py
run_onnx_detection.py
```

역할:

- `onnx_inference.py`: ONNX Runtime 기반 이미지/영상 추론
- `onnx_inference_mqtt.py`: 추론 결과를 MQTT로 publish
- `onnx_detector.py`: YOLOv8 ONNX Runtime detector
- `risk.py`: AMR 안전 주행용 `GO/SLOW/STOP` 위험도 판단
- `run_onnx_detection.py`: 이미지/동영상/웹캠 추론, 결과 영상 저장, MQTT publish

실행 예시:

```powershell
python src/run_onnx_detection.py `
  --model models/best.onnx `
  --source demo/input/warehouse_test.mp4 `
  --output output/detections
```

MQTT publish 예시:

```powershell
python src/run_onnx_detection.py `
  --model models/best.onnx `
  --source demo/input/warehouse_test.mp4 `
  --output output/detections `
  --mqtt-host localhost `
  --mqtt-topic aiot/detection
```
