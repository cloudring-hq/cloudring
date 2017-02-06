# Production Observability Blueprint

Production operation needs more than green deployments. The provider must have
SLOs, alert routing, logs, traces, event capture, retention, and runbooks before
it can be treated as a repeatable private-cloud product.

## Target Stack

- Prometheus Operator owns HA `Prometheus` and `Alertmanager` resources.
- `ServiceMonitor` objects scrape the existing provider-controller and
  provider-portal `/metrics` endpoints in `platform-system`.
- `PrometheusRule` objects alert on provider-controller leader loss, stale
  reconciles, reconcile errors, portal backend errors, cache refresh failures,
  high write throttling, slow summary refreshes, KubeVirt management replica
  loss, and provider portal replica-floor violations.
- A logs/events/traces pipeline uses daemonset node agents plus a deployment
  gateway. OpenTelemetry Collector or Grafana Alloy are suitable choices; both
  preserve the agent/gateway split needed for node telemetry and cluster-wide
  Kubernetes events.
- Loki-compatible log retention must enable compactor retention and use object
  store lifecycle policies longer than the Loki retention window.

## Repository Artifacts

- `iac/kubernetes/production-observability` contains the opt-in blueprint.
- `gitops/platform-production-observability` layers that blueprint over the
  shared platform overlay for real cell promotion.
- `iac/scripts/verify-production-observability-blueprint.ps1` checks the
  blueprint remains opt-in, placeholder-backed, and wired to existing provider
  metrics.

## Production Cutover

1. Install Prometheus Operator, kube-state-metrics, and the selected telemetry
   collector/operator in the target cell.
2. Replace `REPLACE_WITH_*` values, configure remote-write and log/trace
   credentials through a secret manager, and set storage classes/sizes.
3. Render the overlay and run the verifier.
4. Canary one cell, confirm alerts fire in a controlled drill, and validate
   dashboard queries by tenant and platform scope.
5. Promote to additional cells in waves and use Git rollback for alert/rule
   changes.

The Hyper-V lab remains intentionally smaller: it exposes the provider metrics
and runs direct verifiers, but it does not apply the production observability stack by default.
