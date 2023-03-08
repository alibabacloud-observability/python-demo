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


def auto_instrumentation(request):
    return HttpResponse("Hello World!")