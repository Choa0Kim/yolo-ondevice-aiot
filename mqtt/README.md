# MQTT

로컬 실시간 시스템 검증용 Mosquitto 설정입니다.

## Docker 실행

```powershell
docker run -d --name aiot-mosquitto `
  -p 1883:1883 `
  -v ${PWD}\mqtt\mosquitto.conf:/mosquitto/config/mosquitto.conf `
  eclipse-mosquitto:2
```

## Topic

```text
aiot/detection
```

