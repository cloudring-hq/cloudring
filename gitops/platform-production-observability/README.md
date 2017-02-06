# Platform Production Observability Overlay

This overlay layers the production observability blueprint over the shared
platform desired state.

Do not apply it to the current Hyper-V lab as-is. The blueprint expects
Prometheus Operator CRDs, kube-state-metrics, a log/event/tracing backend, and
production secret-manager wiring. Replace all placeholders and run the
observability verifier before promoting a real cell.
