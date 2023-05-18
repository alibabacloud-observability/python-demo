import time
import requests

from opentelemetry import trace
from opentelemetry.exporter.zipkin.encoder import Protocol
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

def init_opentelemetry():
    resource = Resource(attributes={
        SERVICE_NAME: "zipkin-python-demo-v1"
    })

    # create a ZipkinExporter
    zipkin_exporter = ZipkinExporter(
        version=Protocol.V1,
        endpoint="http://tracing-analysis-dc-hz.aliyuncs.com/xxx@xxx@xxx/api/v1/spans",
        max_tag_value_length=256,
        timeout=10,
        session=requests.Session(),
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(zipkin_exporter))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

def inner_method():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("child_span") as child_span:
        print("Hello!")

def outer_method():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("parent_span") as parent_span:
        inner_method()

if __name__ == '__main__':
    init_opentelemetry()
    tracer = trace.get_tracer("my.tracer.name")

    with tracer.start_as_current_span("main") as my_span:
        print(my_span)
        print("Hi!")
        inner_method()

    time.sleep(10)