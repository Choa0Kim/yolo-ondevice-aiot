# 실시간 시스템 검증 가이드

## 1. 목적

학습된 `best.onnx` 모델을 로컬 노트북에서 실행하고, 동영상 프레임 단위 추론 결과를 기반으로 위험도(`GO`, `SLOW`, `STOP`)를 계산한다. 선택적으로 MQTT로 결과를 publish하고 Node-RED 대시보드에서 시각화한다.

## 2. 준비물

필수:

```text
models/best.onnx
```

선택:

```text
demo/input/warehouse_test.mp4
```

모델 파일은 GitHub에 올리지 않는다.

## 3. 패키지 설치

```powershell
python -m pip install -r requirements.txt
```

## 4. 테스트 영상 생성

실제 테스트 영상이 없다면 validation 이미지를 이어붙인 임시 영상을 만들 수 있다.

```powershell
python scripts/create_validation_video.py `
  --source-dir data\processed\dataset_final\images\val `
  --output output\input\validation_slideshow.mp4
```

## 5. ONNX 이미지/동영상 추론

이미지 추론:

```powershell
python src/run_onnx_detection.py `
  --model models\best.onnx `
  --source data\processed\dataset_final\images\val\forklift_val_00000.jpg `
  --output output\detections
```

동영상 추론:

```powershell
python src/run_onnx_detection.py `
  --model models\best.onnx `
  --source output\input\validation_slideshow.mp4 `
  --output output\detections
```

출력:

```text
output/detections/result_video.mp4
```

## 6. 위험도 판단 로직

화면의 중앙 차선과 하단 영역을 기준으로 위험도를 근사한다.

```text
객체 없음 -> GO
객체가 warning zone에 있음 -> SLOW
person/forklift/box/traffic_cone이 중앙 하단 stop zone에 있음 -> STOP
```

이 방식은 실제 거리 센서 없이 단안 카메라 프레임 위치만으로 AMR 근접 위험도를 근사하는 프로토타입 로직이다.

## 7. MQTT 연동

### Mosquitto 실행

```powershell
docker run -d --name aiot-mosquitto `
  -p 1883:1883 `
  -v ${PWD}\mqtt\mosquitto.conf:/mosquitto/config/mosquitto.conf `
  eclipse-mosquitto:2
```

로컬 Python 스크립트는 host 기준으로 `localhost:1883`에 publish한다.

```powershell
python src/run_onnx_detection.py `
  --model models\best.onnx `
  --source output\input\validation_slideshow.mp4 `
  --output output\detections `
  --mqtt-host localhost `
  --mqtt-topic aiot/detection
```

MQTT payload 예시:

```json
{
  "timestamp": "2026-07-05T05:47:35.504590+00:00",
  "device_id": "edge-camera-01",
  "domain": "smart_factory_logistics",
  "objects": [
    {
      "class": "box",
      "confidence": 0.9552,
      "bbox": [309, 323, 428, 454]
    }
  ],
  "risk_level": "STOP",
  "reason": "box detected in center lane stop zone",
  "fps": 8.25,
  "frame_index": 0
}
```

## 8. Node-RED 대시보드

### Node-RED 실행

```powershell
docker run -d --name aiot-node-red -p 1880:1880 nodered/node-red:latest
```

Dashboard 노드 설치:

```powershell
docker exec aiot-node-red npm install node-red-dashboard
docker restart aiot-node-red
```

flow 적용:

```powershell
docker cp node-red\flow.json aiot-node-red:/data/flows.json
docker restart aiot-node-red
```

Node-RED editor:

```text
http://localhost:1880
```

Dashboard:

```text
http://localhost:1880/ui
```

flow의 MQTT broker는 Node-RED 컨테이너 기준으로 `host.docker.internal:1883`을 사용한다.

필요 Node-RED 노드:

```text
node-red-dashboard
```

구독 topic:

```text
aiot/detection
```

대시보드 표시 항목:

```text
Risk Level
FPS
Objects
Reason
Raw payload debug
```

## 9. 현재 로컬 검증 결과

로컬 CPU 기준으로 ONNX Runtime 추론이 정상 동작했다.

검증한 항목:

```text
best.onnx 로드
이미지 추론
동영상 추론
GO/SLOW/STOP 위험도 판단
결과 영상 저장
JSON payload 출력
MQTT publish
Node-RED MQTT broker 연결
```

예시 출력:

```text
output/detections/result_video.mp4
output/detections_mqtt/result_video.mp4
```

검증 당시 컨테이너:

```text
aiot-mosquitto: localhost:1883
aiot-node-red: localhost:1880, dashboard /ui
```

## 10. 실제 작업장 영상 검증 기록

YouTube 작업장/물류 이동 영상 중 04:30-05:00 구간을 테스트 입력으로 사용했다.

```text
source: https://www.youtube.com/watch?v=SA6F75JGd_M
section: 04:30-05:00
local input: demo/input/warehouse_youtube_clip_640_10fps.mp4
output: output/detections_youtube/result_video.mp4
preview: output/detections_youtube/result_video_preview.jpg
```

원본은 1080p 60fps라 로컬 검증 시간이 길어질 수 있어, 시스템 검증용으로 640px 폭/10fps 파일을 별도로 생성했다.

```powershell
python src/run_onnx_detection.py `
  --model models\best.onnx `
  --source demo\input\warehouse_youtube_clip_640_10fps.mp4 `
  --output output\detections_youtube `
  --mqtt-host localhost `
  --mqtt-topic aiot/detection
```

검증 결과:

```text
input frames: 300
input duration: about 30 seconds
output video: created
MQTT publish: confirmed
Node-RED dashboard: confirmed
detected classes: person, box
risk levels: STOP, SLOW
```

대표 payload:

```json
{
  "device_id": "edge-camera-01",
  "domain": "smart_factory_logistics",
  "objects": [
    {
      "class": "person",
      "confidence": 0.7921,
      "bbox": [349, 3, 552, 357]
    },
    {
      "class": "person",
      "confidence": 0.6703,
      "bbox": [134, 94, 379, 359]
    }
  ],
  "risk_level": "STOP",
  "reason": "person detected in center lane stop zone",
  "fps": 8.14,
  "frame_index": 90
}
```

이 검증은 실제 AMR 주행 제어가 아니라, 로컬 노트북에서 ONNX 모델이 동영상 프레임을 처리하고 위험도 판단 결과를 MQTT/Node-RED로 전달할 수 있는지 확인하는 시스템 통합 테스트다.
