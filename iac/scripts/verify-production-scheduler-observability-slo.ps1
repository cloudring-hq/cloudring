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

function Normalize-YamlScalar {
    param([AllowEmptyString()][string]$Value)
    if ($null -eq $Value) {
        return ""
    }
    $normalized = $Value.Trim()
    if ($normalized.Length -ge 2 -and $normalized.StartsWith('"') -and $normalized.EndsWith('"')) {
        return $normalized.Substring(1, $normalized.Length - 2)
    }
    return $normalized
}

function Get-TopLevelMap {
    param(
        [Parameter(Mandatory = $true)][string]$Document,
        [Parameter(Mandatory = $true)][string]$Section
    )
    $map = @{}
    $lines = $Document -split "`r?`n"
    $inSection = $false
    $blockKey = $null
    $blockLines = @()
    foreach ($line in $lines) {
        if ($inSection -and $blockKey -and $line -match "^\s{4,}(.*)$") {
            $blockLines += $Matches[1]
            continue
        }
        if ($inSection -and $blockKey) {
            $map[$blockKey] = ($blockLines -join "`n").TrimEnd()
            $blockKey = $null
            $blockLines = @()
        }
        if ($line -match "^$([regex]::Escape($Section)):\s*$") {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match "^[A-Za-z0-9_-]+:") {
            break
        }
        if ($inSection -and $line -match "^\s{2}([A-Za-z0-9_.\/-]+):\s*\|\s*$") {
            $blockKey = $Matches[1]
            $blockLines = @()
            continue
        }
        if ($inSection -and $line -match "^\s{2}([A-Za-z0-9_.\/-]+):\s*(.*)$") {
            $map[$Matches[1]] = Normalize-YamlScalar $Matches[2]
        }
    }
    if ($inSection -and $blockKey) {
        $map[$blockKey] = ($blockLines -join "`n").TrimEnd()
    }
    return $map
}

function Get-NestedMap {
    param(
        [Parameter(Mandatory = $true)][string]$Document,
        [Parameter(Mandatory = $true)][string]$Parent,
        [Parameter(Mandatory = $true)][string]$Child
    )
    $map = @{}
    $lines = $Document -split "`r?`n"
    $inParent = $false
    $inChild = $false
    foreach ($line in $lines) {
        if ($line -match "^$([regex]::Escape($Parent)):\s*$") {
            $inParent = $true
            continue
        }
        if ($inParent -and $line -match "^[A-Za-z0-9_-]+:") {
            break
        }
        if ($inParent -and $line -match "^\s{2}$([regex]::Escape($Child)):\s*$") {
            $inChild = $true
            continue
        }
        if ($inChild -and $line -match "^\s{2}[A-Za-z0-9_.\/-]+:") {
            break
        }
        if ($inChild -and $line -match "^\s{4}([A-Za-z0-9_.\/-]+):\s*(.*)$") {
            $map[$Matches[1]] = Normalize-YamlScalar $Matches[2]
        }
    }
    return $map
}

function Get-ConfigMapDocument {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Name
    )
    $text = Read-RepoText $RelativePath
    $docs = $text -split "(?m)^---\s*$"
    foreach ($doc in $docs) {
        if ([string]::IsNullOrWhiteSpace($doc)) {
            continue
        }
        if ($doc -notmatch "(?m)^kind:\s*ConfigMap\s*$") {
            continue
        }
        $metadata = Get-TopLevelMap $doc "metadata"
        if ($metadata.ContainsKey("name") -and $metadata["name"] -eq $Name) {
            return $doc
        }
    }
    throw "ConfigMap $Name not found in $RelativePath"
}

function Get-ConfigMapData {
    param([string]$RelativePath, [string]$Name)
    return Get-TopLevelMap (Get-ConfigMapDocument $RelativePath $Name) "data"
}

function Get-ConfigMapAnnotations {
    param([string]$RelativePath, [string]$Name)
    return Get-NestedMap (Get-ConfigMapDocument $RelativePath $Name) "metadata" "annotations"
}

function Require-DataValue {
    param([hashtable]$Data, [string]$Key, [string]$Expected)
    if (-not $Data.ContainsKey($Key)) {
        throw "Missing data key $Key"
    }
    if ($Data[$Key] -ne $Expected) {
        throw "Unexpected value for $Key. Expected '$Expected', got '$($Data[$Key])'"
    }
}

function Require-DataContains {
    param([hashtable]$Data, [string]$Key, [string]$ExpectedSubstring)
    if (-not $Data.ContainsKey($Key)) {
        throw "Missing data key $Key"
    }
    if (-not $Data[$Key].Contains($ExpectedSubstring)) {
        throw "Missing '$ExpectedSubstring' in data key $Key"
    }
}

function Require-DataListContains {
    param([hashtable]$Data, [string]$Key, [string[]]$ExpectedItems)
    if (-not $Data.ContainsKey($Key)) {
        throw "Missing data key $Key"
    }
    $items = @($Data[$Key].Split(",") | ForEach-Object { $_.Trim() })
    foreach ($expected in $ExpectedItems) {
        if ($items -notcontains $expected) {
            throw "Missing list item '$expected' in data key $Key"
        }
    }
}

function Require-Text {
    param([string]$RelativePath, [string[]]$Patterns)
    $text = Read-RepoText $RelativePath
    foreach ($pattern in $Patterns) {
        if (-not $text.Contains($pattern)) {
            throw "Missing pattern '$pattern' in $RelativePath"
        }
    }
}

function Require-TreeNoRegex {
    param([string]$RelativePath, [string]$Pattern, [string]$Message)
    $rootPath = Resolve-RepoPath $RelativePath
    if (-not (Test-Path -LiteralPath $rootPath)) {
        throw "Missing path for boundary scan: $RelativePath"
    }
    $files = @()
    if (Test-Path -LiteralPath $rootPath -PathType Leaf) {
        $files = @(Get-Item -LiteralPath $rootPath)
    } else {
        $files = @(Get-ChildItem -LiteralPath $rootPath -Recurse -File)
    }
    foreach ($file in $files) {
        $text = Get-Content -LiteralPath $file.FullName -Raw
        if ($text -match $Pattern) {
            throw "$Message Offending file: $($file.FullName)"
        }
    }
}

Require-Text "iac\kubernetes\production-scheduler-runtime\kustomization.yaml" @(
    "observability-slo-contract.yaml"
)

$contractPath = "iac\kubernetes\production-scheduler-runtime\observability-slo-contract.yaml"
$sloData = Get-ConfigMapData $contractPath "provider-scheduler-observability-slo-contract"
$sloAnnotations = Get-ConfigMapAnnotations $contractPath "provider-scheduler-observability-slo-contract"
$drillData = Get-ConfigMapData $contractPath "provider-scheduler-observability-slo-drill"
$drillAnnotations = Get-ConfigMapAnnotations $contractPath "provider-scheduler-observability-slo-drill"

Require-DataValue $sloAnnotations "platform.privatecloud.local/template-only" "true"
Require-DataValue $sloAnnotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
Require-DataValue $sloAnnotations "platform.privatecloud.local/observability-slo-contract" "v1"
Require-DataValue $drillAnnotations "platform.privatecloud.local/template-only" "true"
Require-DataValue $drillAnnotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
Require-DataValue $sloData "owner" "provider-scheduler-runtime-controller"
Require-DataValue $sloData "mode-default" "disabled"
Require-DataValue $sloData "health-endpoints" "/healthz,/readyz,/metrics"
Require-DataListContains $sloData "readiness-gates" @(
    "runtimeEnabled",
    "leaderElectionReady",
    "queueLeaseReady",
    "replayLeaseReady",
    "webhookCertificateReady",
    "auditSinkReady"
)
Require-DataListContains $sloData "queue-metrics" @(
    "scheduler_workqueue_depth",
    "scheduler_workqueue_inflight",
    "scheduler_workqueue_retries_total",
    "scheduler_workqueue_deadletter_total",
    "scheduler_workqueue_fairness_throttle_total",
    "scheduler_workqueue_oldest_event_seconds",
    "scheduler_workqueue_wait_seconds"
)
Require-DataListContains $sloData "replay-metrics" @(
    "scheduler_replay_lag_seconds",
    "scheduler_replay_repairs_planned_total",
    "scheduler_replay_repairs_applied_total",
    "scheduler_replay_rejected_total",
    "scheduler_replay_owner_failovers_total"
)
Require-DataListContains $sloData "admission-metrics" @(
    "scheduler_admission_attempts_total",
    "scheduler_admission_latency_seconds",
    "scheduler_admission_rejections_total",
    "scheduler_admission_reservation_conflicts_total",
    "scheduler_admission_quota_conflicts_total"
)
Require-DataListContains $sloData "slo-objectives" @(
    "admission_success_rate_99_9",
    "replay_lag_p99_lt_120s",
    "queue_oldest_event_p99_lt_300s",
    "tenant_fairness_throttle_ratio_lt_5pct",
    "deadletter_rate_lt_0_1pct"
)
Require-DataValue $sloData "burn-rate-windows" "5m,30m,2h,6h"
Require-DataValue $sloData "burn-rate-multipliers" "page_14x_5m,page_6x_30m,ticket_3x_2h,ticket_1x_6h"
Require-DataValue $sloData "slo-thresholds" "admission_success_rate>=99.9,replay_lag_p99_seconds<120,queue_oldest_event_p99_seconds<300,tenant_fairness_throttle_ratio<0.05,deadletter_rate<0.001"
Require-DataContains $sloData "promql-admission-success" "scheduler_admission_rejections_total"
Require-DataContains $sloData "promql-admission-success" "scheduler_admission_attempts_total"
Require-DataContains $sloData "promql-admission-success" "clamp_min"
Require-DataContains $sloData "promql-replay-lag-p99" "scheduler_replay_lag_seconds_bucket"
Require-DataContains $sloData "promql-replay-lag-p99" "histogram_quantile(0.99"
Require-DataContains $sloData "promql-queue-oldest-p99" "scheduler_workqueue_oldest_event_seconds_bucket"
Require-DataContains $sloData "promql-queue-oldest-p99" "projectRef"
Require-DataContains $sloData "promql-tenant-fairness-throttle-ratio" "scheduler_workqueue_fairness_throttle_total"
Require-DataContains $sloData "promql-tenant-fairness-throttle-ratio" "scheduler_workqueue_inflight[5m]"
Require-DataContains $sloData "promql-tenant-fairness-throttle-ratio" "clamp_min"
Require-DataContains $sloData "promql-deadletter-rate" "scheduler_workqueue_deadletter_total"
Require-DataContains $sloData "promql-deadletter-rate" "scheduler_workqueue_retries_total"
Require-DataContains $sloData "promql-deadletter-rate" "clamp_min"
Require-DataListContains $sloData "alert-rules" @(
    "SchedulerRuntimeDown",
    "SchedulerAdmissionErrorBudgetBurn",
    "SchedulerReplayLagHigh",
    "SchedulerWorkQueueBacklogHigh",
    "SchedulerTenantFairnessThrottleHigh",
    "SchedulerDeadLetterRateHigh",
    "SchedulerAuditRetentionSignalMissing"
)
Require-DataValue $sloData "alert-routing" "page=platform-scheduler-primary;ticket=platform-scheduler-secondary;audit=platform-oncall"
Require-DataContains $sloData "alert-severity-map" "SchedulerRuntimeDown=page"
Require-DataContains $sloData "alert-severity-map" "SchedulerDeadLetterRateHigh=ticket"
Require-DataContains $sloData "alert-severity-map" "SchedulerAuditRetentionSignalMissing=page"
Require-DataListContains $sloData "failure-domain-drill-evidence" @(
    "scheduler leader pod deleted",
    "node cordoned",
    "cell marked NotReady",
    "replay owner failed over",
    "queue owner failed over",
    "no duplicate reservation",
    "no cross-tenant mutation"
)
Require-DataListContains $sloData "failure-domain-drill-artifacts" @(
    "leader_pod_delete_event",
    "leader_lease_transition",
    "node_cordon_event",
    "capacity_cell_notready_condition",
    "replay_owner_failover_event",
    "queue_owner_failover_event",
    "reservation_duplicate_absence_report",
    "cross_tenant_mutation_absence_report"
)
Require-DataListContains $sloData "tenant-fairness-dashboard-fields" @(
    "projectRef",
    "namespace",
    "queueDepth",
    "inflight",
    "retries",
    "deadletters",
    "throttleCount",
    "p95WaitSeconds",
    "lastAdmittedAt"
)
Require-DataListContains $sloData "audit-retention-signals" @(
    "AdmissionJournalRetentionFresh",
    "SelfServiceAuditRetentionFresh",
    "SchedulerWorkQueueEventRetentionFresh",
    "SchedulerReplayAuditRetentionFresh"
)
Require-DataValue $sloData "escalation-policy" "platform-scheduler-primary,platform-scheduler-secondary,platform-oncall"
Require-DataContains $sloData "failure-policy" "missing health endpoints"
Require-DataContains $sloData "failure-policy" "missing queue/replay/admission metric families"
Require-DataContains $sloData "failure-policy" "missing owner escalation"
Require-DataContains $drillData "drill" "Production scheduler observability and SLO drill"
Require-DataContains $drillData "drill" "/healthz, /readyz, and /metrics"
Require-DataContains $drillData "drill" "SLO burn-rate windows 5m, 30m, 2h, and 6h"
Require-DataContains $drillData "drill" "leader_pod_delete_event=present"
Require-DataContains $drillData "drill" "leader_lease_transition=incremented"
Require-DataContains $drillData "drill" "reservation_duplicate_absence_report=zero"
Require-DataContains $drillData "drill" "cross_tenant_mutation_absence_report=zero"
Require-DataContains $drillData "drill" "page_14x_5m, page_6x_30m, ticket_3x_2h, and ticket_1x_6h"
Require-DataContains $drillData "drill" "each alert rule has PromQL, severity, and routing owner"
Require-DataContains $drillData "drill" "tenant fairness dashboard fields"
Require-DataContains $drillData "drill" "audit retention freshness signals"

Write-Output "production_scheduler_observability_slo_contract_ok"

$runtimePattern = "observability-slo-contract.yaml|provider-scheduler-observability-slo-contract|provider-scheduler-observability-slo-drill|scheduler-observability-slo|verify-production-scheduler-observability-slo|scheduler_replay_lag_seconds|SchedulerAdmissionErrorBudgetBurn"

Require-TreeNoRegex "gitops\platform" $runtimePattern "The shared lab platform overlay must not apply scheduler observability/SLO resources."
Require-TreeNoRegex "gitops\cells\lab-hyperv" $runtimePattern "The Hyper-V lab cell overlay must not apply scheduler observability/SLO resources."
Require-TreeNoRegex "iac\kubernetes\production-scheduler" $runtimePattern "The contract-only scheduler blueprint must not include scheduler observability/SLO runtime resources."
Require-TreeNoRegex "gitops\platform-production-scheduler" $runtimePattern "The contract-only scheduler overlay must not include scheduler observability/SLO runtime resources."

Write-Output "lab_overlay_no_scheduler_observability_reference_ok"

Require-Text "docs\production-scheduler.md" @(
    "Runtime Observability And SLO Contract",
    "verify-production-scheduler-observability-slo.ps1",
    "SchedulerAdmissionErrorBudgetBurn",
    "tenant fairness dashboard",
    "SchedulerWorkQueueEventRetentionFresh"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\README.md" @(
    "Runtime observability and SLO operations",
    "provider-scheduler-observability-slo-contract",
    "burn-rate",
    "fairness dashboard fields",
    "audit retention freshness"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add production scheduler runtime observability and SLO contract",
    "verify-production-scheduler-observability-slo.ps1"
)

Require-Text "docs\test-plan.md" @(
    "Production scheduler observability and SLO contract",
    "verify-production-scheduler-observability-slo.ps1"
)

Require-Text "docs\operations-log.md" @(
    "Production scheduler observability and SLO contract",
    "verify-production-scheduler-observability-slo.ps1"
)

Write-Output "production_scheduler_observability_slo_fail_closed_ok"
Write-Output "production_scheduler_observability_slo_ok"
