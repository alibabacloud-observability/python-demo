## Python Demo： 手动埋点上报Python应用数据

1. 下载所需包

```
pip install opentelemetry-api
pip install opentelemetry-sdk
pip install opentelemetry-exporter-otlp
```

2. 修改代码中的参数

- service-name: 需要上报的服务名
- host-name：主机名
- endpoint：通过HTTP/gRPC上报数据的接入点
- token：通过gRPC上报数据的鉴权Token

3. 运行

```
python manual.py
```