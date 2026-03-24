# OpenTelemetry Collector Core Distro

This distribution contains all the components from the [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) repository and a small selection of components tied to open source projects from the [OpenTelemetry Collector Contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib) repository.

This distribution is considered "classic" and is no longer accepting new components outside of components from the Core repo.

## Components

The full list of components is available in the [manifest](manifest.yaml)

### Rules for Component Inclusion

Since Core is a "classic" distribution its components are strictly limited to what currently exists in its [manifest](manifest.yaml) and any future components in Core.
No other components from Contrib should be added.


**FINAL OBSERVATION**
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

Workflow in this setup:

Python app → generates spans & increments metrics
OTLP exporter → sends both to otel-collector
Collector:
Traces → Jaeger
Metrics → Prometheus → Grafana
Grafana → visualize numbers & trends
Jaeger → visualize actual spans & error details
