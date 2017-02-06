# Platform Production Scheduler Runtime Overlay

This opt-in GitOps overlay layers `platform-production-scheduler` first and
then adds the disabled-by-default scheduler runtime cutover skeleton from
`iac/kubernetes/production-scheduler-runtime`.

It is intentionally separate from `gitops/platform` and
`gitops/cells/lab-hyperv`; the current Hyper-V lab must not start the runtime
controller or fail-closed admission webhook by default.

Promotion path:

1. Keep the base runtime at `replicas: 0`.
2. Replace the placeholder image and webhook CA bundle through production
   release automation.
3. Apply `canary-enable-patch.example.yaml` to move to one canary replica with
   `RUNTIME_ENABLED=true`.
4. Run the scheduler runtime smoke test and tenant isolation probe.
5. Replace the canary patch with `ha-enable-patch.example.yaml` to run at least
   three replicas only after canary evidence is clean.
