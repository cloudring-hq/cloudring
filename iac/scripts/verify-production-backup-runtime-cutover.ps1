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

Require-Directory "iac\kubernetes\production-backup-runtime" | Out-Null
Require-Directory "gitops\platform-production-backup-runtime" | Out-Null

Require-Text "iac\kubernetes\production-backup-runtime\kustomization.yaml" @(
    "runtime-controller-skeleton.yaml",
    "runtime-cutover-gates.yaml",
    "secret-object-store-contract.yaml",
    "smoke-test-runbook.yaml",
    "rollback-failclosed-runbook.yaml"
)

Require-Text "gitops\platform-production-backup-runtime\kustomization.yaml" @(
    "../platform-production-backup",
    "../../iac/kubernetes/production-backup-runtime"
)

Require-File "gitops\platform-production-backup-runtime\canary-enable-patch.example.yaml" | Out-Null
Require-File "gitops\platform-production-backup-runtime\ha-enable-patch.example.yaml" | Out-Null

Require-NoRegex `
    "iac\kubernetes\production-backup\kustomization.yaml" `
    "production-backup-runtime|runtime-controller-skeleton|runtime-cutover|platform-production-backup-runtime" `
    "The contract-only production-backup bundle must not reference the runtime cutover skeleton."

Require-NoRegex `
    "gitops\platform\kustomization.yaml" `
    "production-backup-runtime|platform-production-backup-runtime" `
    "The shared lab platform overlay must not apply the production backup runtime cutover."

Require-NoRegex `
    "gitops\cells\lab-hyperv\kustomization.yaml" `
    "production-backup-runtime|platform-production-backup-runtime" `
    "The Hyper-V lab cell overlay must not apply the production backup runtime cutover."

Require-Text "iac\kubernetes\production-backup-runtime\runtime-controller-skeleton.yaml" @(
    "kind: ServiceAccount",
    "kind: ClusterRole",
    "kind: ClusterRoleBinding",
    "kind: Deployment",
    "kind: PodDisruptionBudget",
    "kind: Service",
    "provider-backup-runtime-controller",
    "replicas: 0",
    "platform.privatecloud.local/cutover-disabled-by-default: `"true`"",
    "platform.privatecloud.local/promotion-target-replicas: `"3`"",
    "minAvailable: 2",
    "--leader-elect=true",
    '--runtime-enabled=$(RUNTIME_ENABLED)',
    '--canary-scope=$(CANARY_SCOPE)',
    "--fail-closed=true",
    "RUNTIME_ENABLED",
    "value: `"false`"",
    "CANARY_SCOPE",
    "value: disabled",
    "VirtualMachineClaim,Volume,Namespace,KubernetesClusterClaim",
    "EnableCSI",
    "BackupStorageLocation",
    "VolumeSnapshotLocation",
    "BackupRepository",
    "VolumeSnapshotClass",
    "REPLACE_WITH_VERSION",
    "REPLACE_WITH_OBJECT_STORE_SECRET_NAME"
)

Require-Text "iac\kubernetes\production-backup-runtime\runtime-cutover-gates.yaml" @(
    "EnableCSI",
    "node-agent",
    "snapshot-controller",
    "VolumeSnapshotClass",
    "BackupStorageLocation phase Available",
    "VolumeSnapshotLocation reachable",
    "BackupRepository Ready",
    "repository maintenance",
    "object-lock",
    "provider-backup-runtime-controller scales from 0 to 1",
    "RUNTIME_ENABLED=true",
    "CANARY_SCOPE=provider-backup-runtime-canary",
    "provider-backup-runtime-controller scales from 1 to 3",
    "Flux",
    "platform-production-backup-runtime"
)

Require-Text "gitops\platform-production-backup-runtime\canary-enable-patch.example.yaml" @(
    "kind: Deployment",
    "provider-backup-runtime-controller",
    "replicas: 1",
    "RUNTIME_ENABLED",
    "value: `"true`"",
    "CANARY_SCOPE",
    "provider-backup-runtime-canary",
    "RUNTIME_CUTOVER_MODE",
    "canary"
)

Require-Text "gitops\platform-production-backup-runtime\ha-enable-patch.example.yaml" @(
    "kind: Deployment",
    "provider-backup-runtime-controller",
    "replicas: 3",
    "RUNTIME_ENABLED",
    "value: `"true`"",
    "CANARY_SCOPE",
    "production",
    "RUNTIME_CUTOVER_MODE"
)

Require-Text "iac\kubernetes\production-backup-runtime\secret-object-store-contract.yaml" @(
    "production secret manager",
    "no object-store credentials are committed",
    "REPLACE_WITH_OBJECT_STORE_SECRET_NAME",
    "BackupStorageLocation",
    "VolumeSnapshotLocation",
    "Object Lock",
    "fail closed"
)

Require-Text "iac\kubernetes\production-backup-runtime\smoke-test-runbook.yaml" @(
    "velero backup-location get",
    "velero snapshot-location get",
    "velero backup describe",
    "velero restore describe",
    "canary-enable-patch.example.yaml",
    "provider-backup-runtime-controller runs 1/1",
    "RUNTIME_ENABLED=true",
    "ha-enable-patch.example.yaml",
    "provider-backup-runtime-controller runs 3/3",
    "namespaceMapping",
    "resource policies",
    "restore resource modifiers",
    "BackupRepository",
    "tenant isolation probe",
    "cleanup"
)

Require-Text "iac\kubernetes\production-backup-runtime\rollback-failclosed-runbook.yaml" @(
    "replicas: 0",
    "RUNTIME_ENABLED=false",
    "suspend Flux Kustomization",
    "fail closed",
    "do not delete BackupStorageLocation",
    "do not delete BackupRepository",
    "do not unlock object-store retention"
)

Require-Text "docs\production-backup-operations.md" @(
    "production-backup-runtime",
    "platform-production-backup-runtime",
    "verify-production-backup-runtime-cutover.ps1"
)

Require-Text "docs\production-backup-dr.md" @(
    "production-backup-runtime",
    "platform-production-backup-runtime",
    "verify-production-backup-runtime-cutover.ps1"
)

Require-Text "gitops\platform-production-backup-runtime\README.md" @(
    "canary-enable-patch.example.yaml",
    "RUNTIME_ENABLED=true",
    "ha-enable-patch.example.yaml"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add an opt-in production backup runtime cutover skeleton",
    "Implement and validate production backup service runtime integration"
)

Require-Text "docs\scaling-and-performance.md" @(
    "platform-production-backup-runtime",
    "provider-backup-runtime-controller"
)

Require-Text "gitops\README.md" @(
    "platform-production-backup-runtime",
    "production-backup-runtime",
    "verify-production-backup-runtime-cutover.ps1"
)

Write-Output "lab_overlay_no_reference_ok"
Write-Output "contract_bundle_no_runtime_cutover_reference_ok"
Write-Output "production_backup_runtime_cutover_ok"
