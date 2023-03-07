from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPSpanGrpcExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanHttpExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, HOST_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def inner_method():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("child_span") as child_span:
        print("hello world")


def outer_method():
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("parent_span") as parent_span:
        inner_method()


def init_opentelemetry():
    # 设置服务名、主机名
    resource = Resource(attributes={
        SERVICE_NAME: "<service-name>",
        HOST_NAME: "<host-name>"
    })
    # 使用GRPC协议上报
    span_processor = BatchSpanProcessor(OTLPSpanGrpcExporter(
        endpoint="<endpoint>",
        headers=("Authentication=<token>")
    ))
    # 使用HTTP协议上报
    # span_processor = BatchSpanProcessor(OTLPSpanHttpExporter(
    #     endpoint="<endpoint>",
    # ))
    trace_provider = TracerProvider(resource=resource, active_span_processor=span_processor)
    trace.set_tracer_provider(trace_provider)


if __name__ == '__main__':
    init_opentelemetry()
    outer_method()
