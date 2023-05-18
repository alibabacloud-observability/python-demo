## Python Demo： 自动埋点并上报Django应用数据 & 自动埋点与手动埋点结合，上报Django应用数据


### 1. 自动上报Django应用数据
1. 下载所需包
```
pip install django
pip install opentelemetry-sdk
pip install opentelemetry-instrumentation-django
pip install requests
```


2. 创建helloworld app

- 在项目中创建helloworld文件夹

`python manage.py startapp helloworld`

- 在helloworld/views.py中添加代码

```python
from django.http import HttpResponse
from datetime import datetime

# Create your views here.
def hello_world_view(request):
    result = "Hello World! Current Time =" + str(get_time())
    return HttpResponse(result)

def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")
```

- 在helloworld/urls.py中添加代码

```python
from django.urls import path

from . import views

urlpatterns = [
    path('', views.hello_world_view, name='helloworld')
]
```

- 修改 AutoAndManualDemo/urls.py , 添加helloworld的url

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('helloworld/', include('helloworld.urls')),
]
```

3. 在 `manage.py` 修改代码

- 引入包：`from opentelemetry.instrumentation.django import DjangoInstrumentor`
- 在main方法中添加代码：`DjangoInstrumentor().instrument()`

通过如上配置，就可以自动为Django应用埋点。更多信息，请参考 [OpenTelemetry Python Examples: Django Instrumentation](https://opentelemetry-python.readthedocs.io/en/latest/examples/django/README.html)

4. 运行项目

- grpc上报
```
opentelemetry-instrument \
    --traces_exporter console,otlp \
    --service_name <your-service-name> \
    --exporter_otlp_traces_headers="authentication=<token>" \
    --exporter_otlp_traces_endpoint <grpc-endpoint> \
    python manage.py runserver
```

- http上报
```
opentelemetry-instrument \
    --traces_exporter console,otlp_proto_http \
    --service_name <your-service-name> \
    --exporter_otlp_traces_endpoint <http-endpoint> \
    python manage.py runserver
```

### 2. 在自动埋点的基础上手动埋点

1. 下载package
```
pip install opentelemetry-exporter-otlp 

```

1. 修改manage.py代码，添加如下内容（以下内容需放在应用初始化的代码中）
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # 通过gRPC接入
# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter # 通过HTTP接入
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, HOST_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter



resource = Resource(attributes={
        SERVICE_NAME: "<service-name>",
        HOST_NAME: "<host-name>"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(
        endpoint="<endpoint>",
        headers="Authentication=<token>" # 通过gRPC接入时需要headers参数，通过HTTP接入时不需要此参数
)))  # 通过 OTLPSpanExporter 上报Trace
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))  # 在控制台输出Trace
```
- 请替换以下内容，并根据接入方式（gRPC或者HTTP）修改代码
  - `<service-name>`: 需要上报的服务名
  - `<host-name>`：主机名
  - `<endpoint>`：通过HTTP/gRPC上报数据的接入点
  - `<token>`：通过gRPC上报数据的鉴权Token

2. 修改helloworld/views.py代码，获取tracer并手动创建span，同时设置span名称

```python
from django.http import HttpResponse
from opentelemetry import trace
from datetime import datetime


# Create your views here.
def hello_world_view(request):
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("hello_world_span") as hello_world_span:
        result = "Hello World! Current Time =" + str(get_time())
        return HttpResponse(result)


def get_time():
    now = datetime.now()
    tracer = trace.get_tracer(__name__)
    # 创建新的span
    with tracer.start_as_current_span("time_span") as time_span:
        return now.strftime("%H:%M:%S")
```


3. 运行项目

`python manage.py runserver --noreload`

- `--noreload` 防止manage.main方法执行两次
- 如果在运行时出现ImportError(symbol not found in flat namespace '_CFRelease')，请下载grpcio包：
  `pip install grpcio`

4. 在浏览器访问 `127.0.0.1:8000/helloworld`，链路数据便会上报。
