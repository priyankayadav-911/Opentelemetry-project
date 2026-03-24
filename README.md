
         **OpenTelemetry Observability Setup***
**Overview**

This project demonstrates how to implement observability for a Python application using OpenTelemetry. It captures both:

Traces → To see request flow and errors in detail (Jaeger)
Metrics → To monitor counts, error rates, and custom metrics (Prometheus + Grafana)

**Benefits:**

Understand application performance
Detect errors and bottlenecks
Visualize data in real-time dashboards

**Architecture**

         Python App
           │
           │ OTLP Exporter (Traces & Metrics)
           ▼
          OpenTelemetry Collector
           ├─> Jaeger (Traces)
           └─> Prometheus (Metrics)
                   │
                   ▼
                Grafana Dashboard

**Components:**

Component	Purpose
Python App--->Generates traces and metrics, including custom counters and error metrics
OTLP Exporter--->	Sends traces & metrics to collector
OpenTelemetry Collector--->Receives OTLP data and exports it to Jaeger & Prometheus
Jaeger--->View detailed spans and error traces
Prometheus--->Scrapes metrics from collector, provides data for visualization
Grafana--->Creates dashboards and visualizes metrics
**Python Application**
Uses OpenTelemetry SDK for Python
Captures spans (traces) and counters (metrics)
Includes error counters with labels for different error types

**Example snippet:**
app.py:

         from opentelemetry import trace, metrics
         from opentelemetry.sdk.trace import TracerProvider
         from opentelemetry.sdk.trace.export import BatchSpanProcessor
         from opentelemetry.sdk.resources import Resource
         from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        #Setup Tracer
        trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "sample-app"})))
        tracer = trace.get_tracer(__name__)
        span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
        trace.get_tracer_provider().add_span_processor(span_processor)
        #Setup Metrics
        metrics.set_meter_provider(MeterProvider())
        meter = metrics.get_meter(__name__)
        exporter = OTLPMetricExporter(endpoint="localhost:4317", insecure=True)
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=2000)
        metrics.get_meter_provider().start_pipeline(meter, reader)
        #Custom Counter Metrics
        my_counter = meter.create_counter("my_counter_total", description="Number of app requests")
        error_counter = meter.create_counter("error_count_total", description="Number of errors occurred")
        #Application Logic
        with tracer.start_as_current_span("test-span"):
            my_counter.add(1)
            print("Hello OpenTelemetry!")

        try:
            # Simulate an error
            raise ValueError("Random error occurred!")
        except Exception as e:
            error_counter.add(1, {"error_type": type(e).__name__})



# **Collector Configuration 

(otel-collector-config.yaml)


     receivers:
     otlp_grpc:
     otlp_http:

        exporters:
        prometheus:
        endpoint: "0.0.0.0:8889"
        jaeger:
        endpoint: "http://jaeger:14250"
       tls:
      insecure: true

          service:
           pipelines:
             traces:
               receivers: [otlp_grpc, otlp_http]
              exporters: [jaeger]
            metrics:
              receivers: [otlp_grpc, otlp_http]
              exporters: [prometheus]

Notes:

OTLP receivers: Accepts gRPC and HTTP traces/metrics
Jaeger exporter: Receives traces
Prometheus exporter: Exposes metrics on port 8889



**Notes:**

OTLP receivers: Accepts gRPC and HTTP traces/metrics
Jaeger exporter: Receives traces
Prometheus exporter: Exposes metrics on port 8889
**Running the Project**

1️⃣ Start Collector

        docker run -d --name otelcol \
          -v /root/otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml \
          -p 4317-4318:4317-4318 \
          -p 8889:8889 \
          otel/opentelemetry-collector-contrib:0.148.0 \
          --config /etc/otelcol-contrib/config.yaml
2️⃣ Start Jaeger

        docker run -d --name jaeger \
          -p 16686:16686 \
          -p 14250:14250 \
          jaegertracing/all-in-one:1.42
        UI: http://localhost:16686
3️⃣ Start Prometheus

        docker run -d --name prometheus \
          -p 9090:9090 prom/prometheus
           UI: http://localhost:9090
4️⃣ Run Python App

        python3 app.py
        Sends traces → Jaeger
        Sends metrics → Prometheus

**5) Grafana Setup**
      Add Prometheus as a data source
      URL: http://<EC2_IP>:9090
      Create Dashboard Panel

             Metric queries: my_counter_total
                             error_count_total
              Legend: {{error_type}} for error breakdown
              Visualize both metrics in one panel or use multiple panels.

# **How It Works****
Traces: Show request flow and detailed errors in Jaeger
Metrics: Show counts, rates, and error types in Prometheus/Grafana
Combining both allows full observability:
Grafana → “how many errors?”
Jaeger → “what actually failed and where?”
Key Commands
****Check running containers
    docker ps

#Logs for collector
docker logs otelcol -f

#Test Prometheus metrics
curl http://localhost:8889/metrics
Sample Metrics Output
#HELP my_counter_total
#TYPE my_counter_total counter
my_counter_total{job="unknown_service"} 5

#HELP error_count_total
#TYPE error_count_total counter
error_count_total{job="unknown_service",error_type="ValueError"} 2

# **FINAL OBSERVATION**
Grafana + Prometheus: Only shows metrics, i.e., numbers, counters, rates.
Example: my_counter_total = 5 → 5 requests
error_count_total = 2 → 2 errors
It does not show actual error messages or stack traces.
Where you see the actual error?
         Jaeger (traces) → This is where you see detailed spans.
         Each span can have:
         status=error
         Exception messages
         Stack traces
So if you click on a red span in Jaeger, you can see what the error actually was, while Grafana just shows the count of errors.

Think of it like this:
Tool	Shows
Grafana	Metrics (counts, rates, trends)
Prometheus	Scraped metrics (numbers)
Jaeger	Traces (actual operations & errors)

# **Workflow in this setup:**

Python app → generates spans & increments metrics
OTLP exporter → sends both to otel-collector
Collector:
Traces → Jaeger
Metrics → Prometheus → Grafana
Grafana → visualize numbers & trends
Jaeger → visualize actual spans & error details
