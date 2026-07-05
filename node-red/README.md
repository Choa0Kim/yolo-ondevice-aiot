# Node-RED

MQTT 메시지를 구독하고 감지 결과를 시각화하는 Node-RED flow를 보관합니다.

예상 산출물:

```text
flow.json
```

구독 topic:

```text
aiot/detection
```

## 실행

```powershell
docker run -d --name aiot-node-red -p 1880:1880 nodered/node-red:latest
docker exec aiot-node-red npm install node-red-dashboard
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

주의: flow 내부 MQTT broker 주소는 Docker 컨테이너 기준으로 `host.docker.internal`을 사용합니다.
