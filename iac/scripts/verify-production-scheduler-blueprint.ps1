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

Require-Text "iac\kubernetes\production-scheduler\kustomization.yaml" @(
    "namespace.yaml",
    "scheduler-runtime.yaml",
    "multi-cell-placement-policy.yaml",
    "transactional-ledger-contract.yaml"
)

Require-Text "iac\kubernetes\production-scheduler\scheduler-runtime.yaml" @(
    "kind: Deployment",
    "name: provider-scheduler",
    "replicas: 3",
    "kind: PodDisruptionBudget",
    "minAvailable: 2",
    "topologySpreadConstraints:",
    "whenUnsatisfiable: DoNotSchedule",
    "requiredDuringSchedulingIgnoredDuringExecution",
    "REPLACE_WITH_PROVIDER_SCHEDULER_IMAGE",
    "--placement-model=filter-score-reserve-permit",
    "--cell-source=CapacityCell",
    "--reservation-kind=CapacityReservation",
    "--journal-kind=AdmissionJournal",
    "--quota-source=Project.status.quotaUsage",
    "--optimistic-concurrency=resourceVersion",
    "resources: [""leases""]",
    "capacitycells",
    "capacityreservations",
    "admissionjournals"
)

Require-Text "iac\kubernetes\production-scheduler\multi-cell-placement-policy.yaml" @(
    "ProviderPlacementPolicy",
    "VirtualMachineClaim",
    "KubernetesClusterClaim",
    "CapacityCell.status.phase",
    "CapacityReservation.status.phase",
    "AdmissionJournal.spec.decision",
    "Filter",
    "Score",
    "Reserve",
    "Permit",
    "NotReady CapacityCell objects are excluded before scoring.",
    "failure-domain-exact-match",
    "maintenance-drain",
    "scoreWeights:",
    "idempotencyKey: claim UID plus generation"
)

Require-Text "iac\kubernetes\production-scheduler\transactional-ledger-contract.yaml" @(
    "ProviderTransactionalAdmissionContract",
    "CapacityReservation",
    "AdmissionJournal",
    "Project.status.quotaUsage",
    "resourceVersion",
    "project-quota-admission-<projectRef>",
    "capacity-admission-<capacityCell>",
    "provider-scheduler-replay",
    "claim UID plus generation",
    "No backing objects before commit",
    "noBackingObjectsBeforeCommit: true",
    "tenantCannotReadAdmissionJournal: true"
)

Require-Text "gitops\platform-production-scheduler\kustomization.yaml" @(
    "../platform",
    "../../iac/kubernetes/production-scheduler"
)

Require-Text "docs\production-scheduler.md" @(
    "Production Scheduler And Admission Blueprint",
    "does not replace current lab controller runtime",
    "No KubeVirt, CAPI/CAPK, CDI, storage, or network backing object",
    "This blueprint is not a runtime cutover"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add an opt-in production scheduler/admission blueprint",
    "Implement and validate the production scheduler runtime"
)

$crds = Read-RepoText "iac\kubernetes\provider-api\crds.yaml"
foreach ($target in @(
    "kind: CapacityCell",
    "failureDomains:",
    "serviceClasses:",
    "kind: CapacityReservation",
    "enum: [""Active"", ""Released"", ""Expired""]",
    "reservationTTLSeconds:",
    "kind: AdmissionJournal",
    "enum: [""Admitted"", ""Rejected"", ""Pending""]",
    "quotaSnapshot:",
    "locks:",
    "projectQuota:",
    "capacity:",
    "claimRef:",
    "uid:",
    "generation:"
)) {
    if (-not $crds.Contains($target)) {
        throw "Provider API CRD does not expose expected scheduler/admission contract: $target"
    }
}

$labPlatform = Read-RepoText "gitops\platform\kustomization.yaml"
if ($labPlatform -match "production-scheduler|platform-production-scheduler") {
    throw "The shared lab platform overlay must not apply production scheduler by default."
}

$labCell = Read-RepoText "gitops\cells\lab-hyperv\kustomization.yaml"
if ($labCell -match "production-scheduler|platform-production-scheduler") {
    throw "The Hyper-V lab cell overlay must not apply production scheduler by default."
}

Write-Output "production_scheduler_blueprint_ok"
