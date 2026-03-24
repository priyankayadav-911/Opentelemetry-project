from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

import time

# ---- TRACING ----
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({"service.name": "sample-app"})
    )
)

tracer = trace.get_tracer(__name__)

span_processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
)

trace.get_tracer_provider().add_span_processor(span_processor)

# ---- METRICS ----
metric_exporter = OTLPMetricExporter(endpoint="localhost:4317", insecure=True)
reader = PeriodicExportingMetricReader(metric_exporter)

provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter(__name__)

# Create counter
counter = meter.create_counter("my_counter")

import time

while True:
    with tracer.start_as_current_span("test-span"):
        print("Sending data...")
        counter.add(1)
    time.sleep(5)
