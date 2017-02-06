param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    return Join-Path $Root $RelativePath
}

function Require-File {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Resolve-RepoPath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing required file: $RelativePath"
    }
    return $path
}

function Read-RepoText {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    return Get-Content -LiteralPath (Require-File $RelativePath) -Raw
}

function Require-Text {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string[]]$Patterns
    )
    $text = Read-RepoText $RelativePath
    foreach ($pattern in $Patterns) {
        if (-not $text.Contains($pattern)) {
            throw "Missing pattern '$pattern' in $RelativePath"
        }
    }
}

Require-Text "iac\kubernetes\production-observability\kustomization.yaml" @(
    "namespace.yaml",
    "prometheus-stack-contract.yaml",
    "provider-servicemonitors.yaml",
    "provider-alert-rules.yaml",
    "telemetry-pipeline-contract.yaml"
)

Require-Text "iac\kubernetes\production-observability\prometheus-stack-contract.yaml" @(
    "kind: Prometheus",
    "kind: Alertmanager",
    "replicas: 3",
    "replicas: 2",
    "shards: 2",
    "remoteWrite:",
    "REPLACE_WITH_REMOTE_WRITE_URL",
    "REPLACE_WITH_PRODUCTION_BLOCK_STORAGE_CLASS",
    "template-only"
)

Require-Text "iac\kubernetes\production-observability\provider-servicemonitors.yaml" @(
    "kind: ServiceMonitor",
    "name: provider-controller",
    "app.kubernetes.io/name: provider-controller",
    "port: metrics",
    "name: provider-portal",
    "app: provider-portal",
    "path: /metrics"
)

Require-Text "iac\kubernetes\production-observability\provider-alert-rules.yaml" @(
    "kind: PrometheusRule",
    "ProviderControllerShardLeaderMissing",
    "provider_controller_leader",
    "provider_controller_shard_info",
    "ProviderControllerReconcileStale",
    "provider_controller_last_success_timestamp_seconds",
    "provider_controller_reconcile_total{result=`"error`"}",
    "ProviderPortalBackendErrors",
    "provider_portal_write_requests_total",
    "ProviderPortalSummaryRefreshErrors",
    "provider_portal_summary_refresh_errors_total",
    "KubeVirtManagementReplicaLoss",
    "kube_deployment_status_replicas_available",
    "REPLACE_WITH_RUNBOOK_BASE_URL"
)

$alertRules = Read-RepoText "iac\kubernetes\production-observability\provider-alert-rules.yaml"
if ($alertRules.Contains('provider_controller_reconcile_total{result!="success"}')) {
    throw "ProviderControllerReconcileErrors must not treat healthy standby reconciles as errors."
}

Require-Text "iac\kubernetes\production-observability\telemetry-pipeline-contract.yaml" @(
    "provider-telemetry-backends",
    "REPLACE_WITH_LOKI_ENDPOINT",
    "REPLACE_WITH_OTLP_GATEWAY_ENDPOINT",
    "daemonset-agents-plus-deployment-gateway",
    "lokiRetentionMode",
    "compactor-retention-enabled",
    "provider-slo-contract"
)

Require-Text "gitops\platform-production-observability\kustomization.yaml" @(
    "../platform",
    "../../iac/kubernetes/production-observability"
)

Require-Text "docs\production-observability.md" @(
    "Production Observability Blueprint",
    "Prometheus Operator",
    "OpenTelemetry Collector or Grafana Alloy",
    "Loki-compatible log retention",
    "does not apply the production observability stack by default"
)

$providerController = Read-RepoText "iac\kubernetes\provider-controller\controller.py"
foreach ($metric in @(
    "provider_controller_leader",
    "provider_controller_shard_info",
    "provider_controller_reconcile_total",
    "provider_controller_last_success_timestamp_seconds"
)) {
    if (-not $providerController.Contains($metric)) {
        throw "Provider controller metric '$metric' is not present in controller.py"
    }
}

$providerPortal = Read-RepoText "iac\kubernetes\provider-portal\app.py"
foreach ($metric in @(
    "provider_portal_write_requests_total",
    "provider_portal_summary_refresh_errors_total",
    "provider_portal_summary_refresh_seconds",
    "provider_portal_summary_requests_total"
)) {
    if (-not $providerPortal.Contains($metric)) {
        throw "Provider portal metric '$metric' is not present in app.py"
    }
}

$platformOverlay = Read-RepoText "gitops\platform\kustomization.yaml"
if ($platformOverlay -match "production-observability|platform-production-observability") {
    throw "The shared lab platform overlay must not apply production observability by default."
}

$labOverlay = Read-RepoText "gitops\cells\lab-hyperv\kustomization.yaml"
if ($labOverlay -match "production-observability|platform-production-observability") {
    throw "The Hyper-V lab cell overlay must not apply production observability by default."
}

Write-Output "production_observability_blueprint_ok"
