# Data

이 폴더에는 YOLO 학습용 데이터셋 구조와 데이터 설명을 둡니다.

대용량 이미지와 라벨 파일은 GitHub에 직접 올리지 않습니다.

권장 구조:

```text
data/
  images/
    train/
    val/
  labels/
    train/
    val/
  data.yaml
```

초기 클래스:

```yaml
names:
  0: person
  1: car
  2: traffic_cone
  3: obstacle
```

