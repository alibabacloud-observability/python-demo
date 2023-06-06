## Python Demo： 自动埋点并上报Django应用数据 & 自动埋点与手动埋点结合，上报Django应用数据


### 1. 自动上报Django应用数据
1. 下载所需包
```
pip install django
pip install requests
pip install opentelemetry-distro \
	opentelemetry-exporter-otlp
 
opentelemetry-bootstrap -a install
```


2. 创建AutoAndManualDemo项目并创建helloworld app


```python
# 创建AutoAndManualDemo项目
django-admin startproject AutoAndManualDemo

cd AutoAndManualDemo

# 在项目中创建helloworld app
python manage.py startapp helloworld
```



3. 修改代码

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

- 创建helloworld/urls.py文件，在urls.py中添加代码

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

4. 运行项目

- 通过 http 上报
```
opentelemetry-instrument \
    --traces_exporter console,otlp_proto_http \
    --metrics_exporter none \
    --service_name <your-service-name> \
    --exporter_otlp_traces_endpoint <http-endpoint> \
    python manage.py runserver
```

- 请将 <your-service-name> 替换为您的应用名，<http-endpoint>替换为http接入点

- 注意：如果运行报错 `CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False.` 但 AutoAndManualDemo/AutoAndManualDemo/settings.py 中的 DEBUG 和 ALLOWED_HOSTS均已正确配置，这是因为使用 opentelemetry-instrument 启动时使用了danjo框架的默认配置文件 （django/conf/global_settings.py）， 因此需要添加 `export DJANGO_SETTINGS_MODULE=AutoAndManualDemo.settings` 环境变量

5. 浏览器中访问 `http://127.0.0.1:8000/helloworld/`，控制台会打印trace，同时也会将trace上报至阿里云可观测链路OpenTelemetry版。如需关闭



### 2. 手动埋点上报Django应用数据

1. 下载package
```
pip install django
pip install requests
pip install opentelemetry-sdk
pip install opentelemetry-instrumentation-django
pip install opentelemetry-exporter-otlp 

```

2. 创建AutoAndManualDemo项目并创建helloworld app


```python
# 创建AutoAndManualDemo项目
django-admin startproject AutoAndManualDemo

cd AutoAndManualDemo

# 在项目中创建helloworld app
python manage.py startapp helloworld
```


3. 修改helloworld/views.py代码，获取tracer并手动创建span，同时设置span名称

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


4. 修改urls.py文件

- 创建helloworld/urls.py文件，在urls.py中添加代码

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


5. 修改manage.py代码，添加如下内容（以下内容需放在应用初始化的代码中）
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




6. 运行项目

`python manage.py runserver --noreload`

- `--noreload` 防止manage.main方法执行两次
- 如果在运行时出现ImportError(symbol not found in flat namespace '_CFRelease')，请下载grpcio包：
  `pip install grpcio`

7. 在浏览器访问 `127.0.0.1:8000/helloworld`，链路数据便会上报。
