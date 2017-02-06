# Production Observability Blueprint

This directory is an opt-in production observability template for the provider
platform. It is not referenced by the Hyper-V lab overlay.

The blueprint assumes these operators or chart-managed CRDs exist in the target
cell before promotion:

- Prometheus Operator CRDs for `Prometheus`, `Alertmanager`,
  `ServiceMonitor`, and `PrometheusRule`.
- A kube-state-metrics source for Kubernetes object health alerts.
- A logs/events/traces pipeline such as OpenTelemetry Collector or Grafana
  Alloy, with Loki-compatible log retention and an OTLP gateway.
- A production secret manager for remote-write, Loki, and OTLP credentials.

The current lab already exposes provider-controller and provider-portal
Prometheus-style metrics. This blueprint wires those existing metrics into the
production scrape and alert contract without applying the monitoring stack to
the small nested Hyper-V sandbox by default.

## Promotion Checklist

1. Install the required observability CRDs/operators in the target cell.
2. Replace every `REPLACE_WITH_*` placeholder and move credentials into a
   secret manager.
3. Decide the Prometheus shard/replica/storage profile for the cell size.
4. Render the overlay and run `iac/scripts/verify-production-observability-blueprint.ps1`.
5. Promote through GitOps after a canary cell proves alerts, dashboards, log
   retention, and notification routing.
