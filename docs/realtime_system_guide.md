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
