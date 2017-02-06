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

Require-Text "iac\kubernetes\production-backup\kustomization.yaml" @(
    "backup-runtime-operations-contract.yaml",
    "restore-drill-slo-contract.yaml",
    "tenant-restore-isolation-policy.yaml"
)

Require-Text "iac\kubernetes\production-backup\backup-runtime-operations-contract.yaml" @(
    "provider-backup-runtime-operations-contract",
    "contract-only-not-lab-runtime-cutover",
    "Velero EnableCSI with CSI snapshot data movement",
    "BackupRepository per protected namespace",
    "Repository maintenance jobs",
    "Backup phase Complete",
    "Backup remains Finalizing",
    "backup_plan_rpo_violation_total",
    "velero_backup_repository_phase",
    "Fail closed for unknown tenant authorization"
)

Require-Text "iac\kubernetes\production-backup\restore-drill-slo-contract.yaml" @(
    "provider-restore-drill-slo-contract",
    "VirtualMachineClaim: 24h",
    "Volume: 1h",
    "KubernetesClusterClaim: 4h",
    "BackupStorageLocation phase Available",
    "VolumeSnapshotLocation reachable",
    "BackupRepository is Ready",
    "Resource filtering or resource policies",
    "namespaceMapping is present",
    "Restore resource modifiers",
    "velero backup describe",
    "tenant isolation probe"
)

Require-Text "iac\kubernetes\production-backup\tenant-restore-isolation-policy.yaml" @(
    "provider-tenant-restore-isolation-policy",
    "Project.spec.adminsGroup plus token namespace scope",
    "RestoreRequest status and SelfServiceAuditEvent",
    "namespaceMapping is required",
    "default-deny NetworkPolicy",
    "Use Velero includedNamespaces, includedResources, excludedResources, or resource policies",
    "Exclude cluster-scoped RBAC, StorageClass, CRD, webhook, and APF objects",
    "Restore resource modifiers must rewrite namespace",
    "Deny cross-tenant restore",
    "Deny in-place restore without provider-admin approval"
)

Require-Text "docs\production-backup-operations.md" @(
    "Production Backup Runtime Operations",
    "BackupRepository",
    "repository maintenance",
    "Object-lock or equivalent retention",
    "namespaceMapping",
    "resource filtering or resource policies",
    "restore resource modifiers",
    "does not install or run a production backup service in the lab"
)

Require-Text "docs\production-backup-dr.md" @(
    "Production Backup Runtime Operations",
    "service ownership, preflight gates, SLOs, restore drills, and tenant isolation"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add an opt-in production backup runtime operations contract",
    "Implement and validate production backup service runtime integration"
)

$crds = Read-RepoText "iac\kubernetes\provider-api\crds.yaml"
foreach ($target in @(
    'enum: ["VirtualMachineClaim", "KubernetesClusterClaim", "Volume", "Namespace"]',
    'enum: ["local", "remote", "immutable"]',
    'kind: BackupPlan',
    'kind: RestoreRequest'
)) {
    if (-not $crds.Contains($target)) {
        throw "Provider API CRD does not expose expected backup runtime contract: $target"
    }
}

$labPlatform = Read-RepoText "gitops\platform\kustomization.yaml"
if ($labPlatform -match "production-backup|platform-production-backup|production-backup-runtime|platform-production-backup-runtime") {
    throw "The shared lab platform overlay must not apply production backup runtime operations by default."
}

$labCell = Read-RepoText "gitops\cells\lab-hyperv\kustomization.yaml"
if ($labCell -match "production-backup|platform-production-backup|production-backup-runtime|platform-production-backup-runtime") {
    throw "The Hyper-V lab cell overlay must not apply production backup runtime operations by default."
}

Write-Output "production_backup_runtime_blueprint_ok"
