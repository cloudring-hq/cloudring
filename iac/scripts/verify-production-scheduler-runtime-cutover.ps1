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

function Require-Directory {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Resolve-RepoPath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        throw "Missing required directory: $RelativePath"
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

Require-Directory "iac\kubernetes\production-scheduler-runtime" | Out-Null
Require-Directory "gitops\platform-production-scheduler-runtime" | Out-Null

Require-Text "iac\kubernetes\production-scheduler-runtime\kustomization.yaml" @(
    "runtime-controller-skeleton.yaml",
    "admission-webhook-failclosed.yaml",
    "runtime-cutover-gates.yaml",
    "smoke-test-runbook.yaml",
    "rollback-failclosed-runbook.yaml"
)

Require-Text "gitops\platform-production-scheduler-runtime\kustomization.yaml" @(
    "../platform-production-scheduler",
    "../../iac/kubernetes/production-scheduler-runtime"
)

Require-File "gitops\platform-production-scheduler-runtime\canary-enable-patch.example.yaml" | Out-Null
Require-File "gitops\platform-production-scheduler-runtime\ha-enable-patch.example.yaml" | Out-Null

$runtimePattern = "production-scheduler-runtime|platform-production-scheduler-runtime|provider-scheduler-runtime-controller|provider-scheduler-admission-webhook"

Require-NoRegex `
    "gitops\platform\kustomization.yaml" `
    $runtimePattern `
    "The shared lab platform overlay must not apply the production scheduler runtime cutover."

Require-NoRegex `
    "gitops\cells\lab-hyperv\kustomization.yaml" `
    $runtimePattern `
    "The Hyper-V lab cell overlay must not apply the production scheduler runtime cutover."

Write-Output "lab_overlay_no_scheduler_runtime_cutover_reference_ok"

Require-NoRegex `
    "iac\kubernetes\production-scheduler\kustomization.yaml" `
    $runtimePattern `
    "The contract-only production scheduler blueprint must not reference the runtime cutover skeleton."

Require-NoRegex `
    "gitops\platform-production-scheduler\kustomization.yaml" `
    $runtimePattern `
    "The contract-only production scheduler overlay must not reference the runtime cutover skeleton."

Write-Output "contract_overlay_no_scheduler_runtime_cutover_reference_ok"

Require-Text "iac\kubernetes\production-scheduler-runtime\runtime-controller-skeleton.yaml" @(
    "kind: ServiceAccount",
    "kind: ClusterRole",
    "kind: ClusterRoleBinding",
    "kind: Deployment",
    "kind: PodDisruptionBudget",
    "kind: Service",
    "provider-scheduler-runtime-controller",
    "namespace: platform-scheduler",
    "replicas: 0",
    'platform.privatecloud.local/cutover-disabled-by-default: "true"',
    'platform.privatecloud.local/promotion-target-replicas: "3"',
    "minAvailable: 2",
    "--leader-elect=true",
    "--leader-election-lease=provider-scheduler-runtime-controller",
    '--runtime-enabled=$(RUNTIME_ENABLED)',
    '--canary-scope=$(CANARY_SCOPE)',
    "--fail-closed=true",
    "--admission-webhook-mode=fail-closed",
    "--placement-model=filter-score-reserve-permit",
    "--reservation-kind=CapacityReservation",
    "--journal-kind=AdmissionJournal",
    "--quota-source=Project.status.quotaUsage",
    "--webhook-address=:9443",
    "RUNTIME_ENABLED",
    'value: "false"',
    "CANARY_SCOPE",
    "value: disabled",
    "RUNTIME_CUTOVER_MODE",
    "value: fail-closed",
    "REPLACE_WITH_PROVIDER_SCHEDULER_RUNTIME_IMAGE"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\admission-webhook-failclosed.yaml" @(
    "kind: ValidatingWebhookConfiguration",
    "provider-scheduler-admission-webhook",
    "failurePolicy: Fail",
    "sideEffects: None",
    "timeoutSeconds: 5",
    "namespaceSelector:",
    "platform.privatecloud.local/scheduler-runtime-webhook: enabled",
    "objectSelector:",
    "platform.privatecloud.local/scheduler-runtime-admission: enabled",
    "admissionReviewVersions:",
    "- v1",
    "caBundle: REPLACE_WITH_PROVIDER_SCHEDULER_WEBHOOK_CA_BUNDLE",
    "provider-scheduler-runtime-webhook",
    "virtualmachineclaims",
    "kubernetesclusterclaims",
    "capacityreservations",
    "admissionjournals",
    "projects"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\runtime-cutover-gates.yaml" @(
    "verify-production-scheduler-blueprint.ps1",
    "verify-production-scheduler-runtime-admission-seam.ps1",
    "CapacityCell Ready",
    "CapacityReservation CRD",
    "AdmissionJournal CRD",
    "project-quota-admission",
    "capacity-admission",
    "provider-scheduler-admission-webhook certificates",
    "namespaceSelector and objectSelector opt-in labels",
    "provider-scheduler-runtime-controller scales from 0 to 1",
    "RUNTIME_ENABLED=true",
    "provider-scheduler-runtime-controller scales from 1 to 3",
    "Flux",
    "platform-production-scheduler-runtime"
)

Require-Text "gitops\platform-production-scheduler-runtime\canary-enable-patch.example.yaml" @(
    "kind: Deployment",
    "provider-scheduler-runtime-controller",
    "replicas: 1",
    "RUNTIME_ENABLED",
    'value: "true"',
    "CANARY_SCOPE",
    "provider-scheduler-runtime-canary",
    "RUNTIME_CUTOVER_MODE",
    "canary"
)

Require-Text "gitops\platform-production-scheduler-runtime\ha-enable-patch.example.yaml" @(
    "kind: Deployment",
    "provider-scheduler-runtime-controller",
    "replicas: 3",
    "RUNTIME_ENABLED",
    'value: "true"',
    "CANARY_SCOPE",
    "production",
    "RUNTIME_CUTOVER_MODE",
    "ha"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\smoke-test-runbook.yaml" @(
    "verify-production-scheduler-runtime-admission-seam.ps1",
    "kubectl get capacitycells",
    "kubectl get capacityreservations",
    "kubectl get admissionjournals",
    "provider-scheduler-runtime-controller runs 1/1",
    "RUNTIME_ENABLED=true",
    "platform.privatecloud.local/scheduler-runtime-webhook=enabled",
    "platform.privatecloud.local/scheduler-runtime-admission=enabled",
    "canary-enable-patch.example.yaml",
    "ha-enable-patch.example.yaml",
    "provider-scheduler-runtime-controller runs 3/3",
    "tenant isolation probe",
    "cleanup"
)

Require-Text "iac\kubernetes\production-scheduler-runtime\rollback-failclosed-runbook.yaml" @(
    "replicas: 0",
    "RUNTIME_ENABLED=false",
    "suspend Flux Kustomization",
    "fail closed",
    "do not delete CapacityReservation",
    "do not delete AdmissionJournal",
    "do not delete CapacityCell"
)

Require-Text "docs\production-scheduler.md" @(
    "production-scheduler-runtime",
    "platform-production-scheduler-runtime",
    "verify-production-scheduler-runtime-cutover.ps1"
)

Require-Text "gitops\README.md" @(
    "platform-production-scheduler-runtime",
    "production-scheduler-runtime",
    "verify-production-scheduler-runtime-cutover.ps1"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add an opt-in production scheduler runtime cutover skeleton",
    "Implement and validate the production scheduler runtime"
)

Require-Text "docs\test-plan.md" @(
    "Production scheduler runtime cutover skeleton",
    "verify-production-scheduler-runtime-cutover.ps1"
)

Require-Text "docs\operations-log.md" @(
    "Production scheduler runtime cutover skeleton",
    "verify-production-scheduler-runtime-cutover.ps1"
)

Write-Output "production_scheduler_runtime_cutover_ok"
