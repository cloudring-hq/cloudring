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

function Require-NoRegex {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $text = Read-RepoText $RelativePath
    if ($text -match $Pattern) {
        throw $Message
    }
}

function Get-ConfigMapData {
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
        if (-not $metadata.ContainsKey("name") -or $metadata["name"] -ne $Name) {
            continue
        }
        return Get-TopLevelMap $doc "data"
    }
    throw "ConfigMap $Name not found in $RelativePath"
}

function Get-ConfigMapAnnotations {
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
        if (-not $metadata.ContainsKey("name") -or $metadata["name"] -ne $Name) {
            continue
        }
        return Get-NestedMap $doc "metadata" "annotations"
    }
    throw "ConfigMap $Name not found in $RelativePath"
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
            $key = $Matches[1]
            $value = Normalize-YamlScalar $Matches[2]
            $map[$key] = $value
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

function Require-DataValue {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Data,
        [Parameter(Mandatory = $true)][string]$Key,
        [Parameter(Mandatory = $true)][string]$Expected
    )
    if (-not $Data.ContainsKey($Key)) {
        throw "Missing data key $Key"
    }
    if ($Data[$Key] -ne $Expected) {
        throw "Unexpected value for $Key. Expected '$Expected', got '$($Data[$Key])'"
    }
}

function Require-DataContains {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Data,
        [Parameter(Mandatory = $true)][string]$Key,
        [Parameter(Mandatory = $true)][string]$ExpectedSubstring
    )
    if (-not $Data.ContainsKey($Key)) {
        throw "Missing data key $Key"
    }
    if (-not $Data[$Key].Contains($ExpectedSubstring)) {
        throw "Missing '$ExpectedSubstring' in data key $Key"
    }
}

function Require-TreeNoRegex {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )
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
    "workqueue-runtime-contract.yaml"
)

$queueData = Get-ConfigMapData `
    "iac\kubernetes\production-scheduler-runtime\workqueue-runtime-contract.yaml" `
    "provider-scheduler-workqueue-runtime-contract"
$queueAnnotations = Get-ConfigMapAnnotations `
    "iac\kubernetes\production-scheduler-runtime\workqueue-runtime-contract.yaml" `
    "provider-scheduler-workqueue-runtime-contract"
$drillData = Get-ConfigMapData `
    "iac\kubernetes\production-scheduler-runtime\workqueue-runtime-contract.yaml" `
    "provider-scheduler-workqueue-drill"
$drillAnnotations = Get-ConfigMapAnnotations `
    "iac\kubernetes\production-scheduler-runtime\workqueue-runtime-contract.yaml" `
    "provider-scheduler-workqueue-drill"

Require-Text "iac\kubernetes\production-scheduler-runtime\workqueue-runtime-contract.yaml" @(
    "provider-scheduler-workqueue-runtime-contract",
    "provider-scheduler-workqueue-drill"
)

Require-DataValue $queueAnnotations "platform.privatecloud.local/template-only" "true"
Require-DataValue $queueAnnotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
Require-DataValue $queueAnnotations "platform.privatecloud.local/workqueue-runtime-contract" "v1"
Require-DataValue $drillAnnotations "platform.privatecloud.local/template-only" "true"
Require-DataValue $drillAnnotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
Require-DataValue $queueData "queue-owner" "provider-scheduler-runtime-controller"
Require-DataValue $queueData "queue-mode-default" "disabled"
Require-DataValue $queueData "queue-lease-name" "provider-scheduler-runtime-workqueue-owner"
Require-DataValue $queueData "queue-lease-namespace" "platform-scheduler"
Require-DataValue $queueData "event-sources" "VirtualMachineClaim,KubernetesClusterClaim,Project,CapacityCell,CapacityReservation,AdmissionJournal"
Require-DataValue $queueData "durable-event-ledger-kind" "SchedulerWorkQueueEvent"
Require-DataValue $queueData "durable-event-ledger-scope" "cluster"
Require-DataValue $queueData "event-ordering" "namespace,projectRef,claimKind,claimName,claimUID,generation,resourceVersion"
Require-DataValue $queueData "idempotency-key" "claimUID:generation:resourceVersion:eventReason"
Require-DataValue $queueData "duplicate-policy" "suppress duplicate idempotency keys before Filter or Reserve"
Require-DataValue $queueData "tenant-fairness-policy" "weighted-round-robin per projectRef with max 4 consecutive events per project"
Require-DataValue $queueData "max-inflight-per-project" "2"
Require-DataValue $queueData "max-inflight-global" "16"
Require-DataValue $queueData "backoff-policy" "exponential 5s,15s,45s,2m,5m with jitter"
Require-DataValue $queueData "dead-letter-after-attempts" "5"
Require-DataValue $queueData "dead-letter-sink" "provider-scheduler-workqueue-deadletter"
Require-DataValue $queueData "promotion-phases" "disabled,dry-run,canary-consume,ha-consume"
Require-DataContains $queueData "failover-handoff" "unacked SchedulerWorkQueueEvent records"
Require-DataContains $queueData "mutation-boundary" "audit/metric records only"
Require-DataContains $queueData "tenant-isolation-invariant" "cross-tenant queue keys are rejected before enqueue"
Require-DataContains $queueData "metrics" "scheduler_workqueue_depth"
Require-DataContains $queueData "metrics" "scheduler_workqueue_deadletter_total"
Require-DataContains $queueData "audit-events" "WorkQueueEventAccepted"
Require-DataContains $queueData "audit-events" "WorkQueueDuplicateSuppressed"
Require-DataContains $queueData "audit-events" "WorkQueueBackoffScheduled"
Require-DataContains $queueData "audit-events" "WorkQueueDeadLettered"
Require-DataContains $queueData "audit-events" "WorkQueueOwnerFailover"
Require-DataContains $queueData "audit-events" "WorkQueueTenantThrottled"
Require-DataContains $queueData "failure-policy" "missing queue owner"
Require-DataContains $queueData "failure-policy" "cross-tenant queue key"
Require-DataContains $drillData "drill" "Production scheduler work-queue drill"
Require-DataContains $drillData "drill" "weighted round robin prevents tenant starvation"
Require-DataContains $drillData "drill" "WorkQueueDuplicateSuppressed before Filter or"
Require-DataContains $drillData "drill" "dead-letter after five attempts"
Require-DataContains $drillData "drill" "WorkQueueOwnerFailover and replay unacked SchedulerWorkQueueEvent"

Write-Output "production_scheduler_workqueue_contract_ok"

$runtimePattern = "provider-scheduler-workqueue-runtime-contract|provider-scheduler-workqueue-drill|provider-scheduler-runtime-workqueue-owner|scheduler-workqueue-runtime|verify-production-scheduler-workqueue-runtime|scheduler_workqueue_"

Require-TreeNoRegex `
    "gitops\platform" `
    $runtimePattern `
    "The shared lab platform overlay must not apply scheduler work-queue runtime resources."

Require-TreeNoRegex `
    "gitops\cells\lab-hyperv" `
    $runtimePattern `
    "The Hyper-V lab cell overlay must not apply scheduler work-queue runtime resources."

Require-TreeNoRegex `
    "iac\kubernetes\production-scheduler" `
    $runtimePattern `
    "The contract-only scheduler blueprint must not include scheduler work-queue runtime resources."

Require-TreeNoRegex `
    "gitops\platform-production-scheduler" `
    $runtimePattern `
    "The contract-only scheduler overlay must not include scheduler work-queue runtime resources."

Write-Output "lab_overlay_no_scheduler_workqueue_reference_ok"

Require-Text "docs\production-scheduler.md" @(
    "Runtime Work-Queue Contract",
    "verify-production-scheduler-workqueue-runtime.ps1",
    "provider-scheduler-runtime-workqueue-owner",
    "SchedulerWorkQueueEvent",
    "WorkQueueDuplicateSuppressed",
    "WorkQueueDeadLettered",
    "WorkQueueOwnerFailover"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\README.md" @(
    "Runtime work-queue operations",
    "provider-scheduler-workqueue-runtime-contract",
    "provider-scheduler-runtime-workqueue-owner",
    "SchedulerWorkQueueEvent",
    "weighted-round-robin",
    "dead-letter",
    "ha-consume"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add production scheduler work-queue runtime contract",
    "verify-production-scheduler-workqueue-runtime.ps1"
)

Require-Text "docs\test-plan.md" @(
    "Production scheduler work-queue runtime contract",
    "verify-production-scheduler-workqueue-runtime.ps1"
)

Require-Text "docs\operations-log.md" @(
    "Production scheduler work-queue runtime contract",
    "verify-production-scheduler-workqueue-runtime.ps1"
)

Write-Output "production_scheduler_workqueue_fail_closed_ok"
Write-Output "production_scheduler_workqueue_runtime_ok"
