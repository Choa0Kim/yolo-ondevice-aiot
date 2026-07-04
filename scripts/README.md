# Scripts

로컬 데이터셋 생성, 검증, 병합에 사용하는 스크립트를 보관합니다.

## prepare_openimages_person_box.py

Open Images V7에서 `Person`, `Box` 샘플만 다운로드하고 프로젝트 YOLO 클래스 ID로 변환합니다.

출력 위치:

```text
data/processed/openimages_person_box_yolo/
```

실행 예시:

```powershell
python scripts/prepare_openimages_person_box.py --source-samples 300 --train-per-class 64 --val-per-class 16
```

생성되는 클래스 ID:

```text
0: person
1: box
2: traffic_cone
3: forklift
```

## check_yolo_dataset.py

YOLO 데이터셋의 이미지 수, 라벨 수, 클래스별 객체 수를 확인합니다.

실행 예시:

```powershell
python scripts/check_yolo_dataset.py data\processed\openimages_person_box_yolo
```

## train_yolov8.py

YOLOv8 모델을 학습합니다.

Colab 예시:

```bash
python scripts/train_yolov8.py \
  --data /content/dataset_final/data.yaml \
  --epochs 30 \
  --batch 8 \
  --project /content/runs \
  --name logistics_yolov8n
```

## predict_validation.py

학습된 모델로 validation 이미지 예측 결과를 저장합니다.

```bash
python scripts/predict_validation.py \
  --model /content/runs/logistics_yolov8n/weights/best.pt \
  --source /content/dataset_final/images/val \
  --project /content/runs \
  --name val_predictions
```

## export_onnx.py

학습된 `best.pt`를 ONNX로 변환합니다.

```bash
python scripts/export_onnx.py \
  --model /content/runs/logistics_yolov8n/weights/best.pt \
  --imgsz 640
```

## merge_yolo_datasets.py

여러 YOLO 데이터셋을 최종 클래스 ID 체계로 재매핑하면서 병합합니다.

최종 클래스 ID:

```text
0: person
1: box
2: traffic_cone
3: forklift
```

`person/box` 중간 데이터셋을 최종 데이터셋에 병합하는 예시:

```powershell
python scripts/merge_yolo_datasets.py `
  --source data\processed\openimages_person_box_yolo `
  --target data\processed\dataset_final `
  --class-map 0:0,1:1 `
  --prefix person_box
```

`traffic_cone`만 있는 데이터셋의 원본 클래스 ID가 `0`인 경우:

```powershell
python scripts/merge_yolo_datasets.py `
  --source data\processed\traffic_cone_yolo `
  --target data\processed\dataset_final `
  --class-map 0:2 `
  --prefix traffic_cone
```

## download_roboflow_yolo.py

Roboflow 데이터셋을 YOLOv8 형식으로 다운로드합니다. API key는 코드에 직접 쓰지 않고 `ROBOFLOW_API_KEY` 환경변수로 전달합니다.

traffic cone 데이터셋 다운로드 예시:

```powershell
$env:ROBOFLOW_API_KEY="YOUR_API_KEY"
python scripts/download_roboflow_yolo.py `
  --workspace mail-vanbergeijk `
  --project frc2023-935 `
  --version 4 `
  --output-dir data\processed\traffic_cone_yolo
```

## normalize_roboflow_yolo.py

Roboflow YOLOv8 export 구조를 프로젝트 표준 YOLO 구조로 변환합니다. `valid` split은 `val`로 바꾸고, 필요한 클래스만 최종 클래스 ID로 재매핑합니다.

traffic cone 데이터셋 정규화 예시:

```powershell
python scripts/normalize_roboflow_yolo.py `
  --source data\processed\traffic_cone_yolo `
  --target data\processed\traffic_cone_yolo_normalized `
  --class-map 0:2 `
  --prefix traffic_cone
```
