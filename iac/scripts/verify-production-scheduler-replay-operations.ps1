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

Require-Text "iac\kubernetes\production-scheduler-runtime\kustomization.yaml" @(
    "replay-operations-contract.yaml"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\replay-operations-contract.yaml" @(
    "provider-scheduler-replay-operations-contract",
    "platform.privatecloud.local/template-only",
    "platform.privatecloud.local/cutover-disabled-by-default",
    "controller-owner: provider-scheduler-runtime-controller",
    "replay-mode-default: dry-run",
    "replay-lease-name: provider-scheduler-runtime-replay-owner",
    "replay-lease-namespace: platform-scheduler",
    "replay-lease-duration: 30s",
    "replay-renew-deadline: 20s",
    "replay-retry-period: 5s",
    "failover-grace-window: 45s",
    "repair-window-default: maintenance-only",
    "replay-retention-boundary: replay windows must not exceed AdmissionJournal and CapacityReservation retention",
    "promotion-phases: disabled,dry-run,canary-apply,ha-apply",
    "canary-availability-caveat: canary replicas=1 is for smoke only and must not be treated as HA while the runtime PDB expects minAvailable=2",
    "green quota replay verifier",
    "green admission seam verifier",
    "tenant-isolation-invariant: projectRef namespace must equal request namespace",
    "mutation-boundary: only CapacityReservation status, Project status, claim status, and provider audit Events may be patched during apply phases",
    "audit-events: ReplayDryRunStarted,ReplayDecisionReconstructed,ReplayRepairPlanned,ReplayRepairApplied,ReplayRejected,ReplayFailoverObserved,ReplayLeaseLost",
    "failure-policy: fail-closed on missing lease settings, unsafe repair window, invalid promotion phase, missing audit taxonomy, or tenant scope mismatch",
    "rollback-policy: return to dry-run, scale runtime controller to 0, keep AdmissionJournal and CapacityReservation history intact",
    "Production scheduler replay failover drill",
    "exactly one holder for Lease",
    "verify-production-scheduler-quota-replay-seam.ps1",
    "ReplayFailoverObserved",
    "Reject replay windows longer than AdmissionJournal or",
    "ReplayRejected and no repair action",
    "must not read AdmissionJournal or replay lease objects",
    "one-replica canary as a smoke phase only"
)

Write-Output "production_scheduler_replay_operations_contract_ok"

$runtimePattern = "provider-scheduler-replay-operations-contract|provider-scheduler-replay-failover-drill|provider-scheduler-runtime-replay-owner|scheduler-replay-operations|verify-production-scheduler-replay-operations"

Require-NoRegex `
    "gitops\platform\kustomization.yaml" `
    $runtimePattern `
    "The shared lab platform overlay must not apply scheduler replay operations."

Require-NoRegex `
    "gitops\cells\lab-hyperv\kustomization.yaml" `
    $runtimePattern `
    "The Hyper-V lab cell overlay must not apply scheduler replay operations."

Require-NoRegex `
    "iac\kubernetes\production-scheduler\kustomization.yaml" `
    $runtimePattern `
    "The contract-only scheduler blueprint must not include scheduler replay operations runtime resources."

Require-NoRegex `
    "gitops\platform-production-scheduler\kustomization.yaml" `
    $runtimePattern `
    "The contract-only scheduler overlay must not include scheduler replay operations runtime resources."

Write-Output "lab_overlay_no_scheduler_replay_operations_reference_ok"

Require-Text "docs\production-scheduler.md" @(
    "Runtime Replay Operations Contract",
    "verify-production-scheduler-replay-operations.ps1",
    "provider-scheduler-runtime-replay-owner",
    "ReplayDryRunStarted",
    "ReplayFailoverObserved",
    "ReplayRejected"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\README.md" @(
    "Runtime replay operations",
    "provider-scheduler-replay-operations-contract",
    "dry-run",
    "provider-scheduler-runtime-replay-owner",
    "canary-apply",
    "ha-apply"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add scheduler replay operations and failover contract",
    "verify-production-scheduler-replay-operations.ps1"
)

Require-Text "docs\test-plan.md" @(
    "Production scheduler replay operations contract",
    "verify-production-scheduler-replay-operations.ps1"
)

Require-Text "docs\operations-log.md" @(
    "Production scheduler replay operations contract",
    "verify-production-scheduler-replay-operations.ps1"
)

Write-Output "production_scheduler_replay_operations_fail_closed_ok"
Write-Output "production_scheduler_replay_operations_ok"
