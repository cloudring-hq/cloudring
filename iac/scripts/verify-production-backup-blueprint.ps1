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
    "csi-snapshot-classes.yaml",
    "velero-schedules.yaml",
    "provider-backupplan-examples.yaml",
    "restore-workflow-contract.yaml"
)

Require-Text "iac\kubernetes\production-backup\csi-snapshot-classes.yaml" @(
    "kind: VolumeSnapshotClass",
    "provider-production-csi-retain",
    "deletionPolicy: Retain",
    "provider-production-csi-delete",
    "REPLACE_WITH_PRODUCTION_CSI_DRIVER"
)

Require-Text "iac\kubernetes\production-backup\velero-schedules.yaml" @(
    "kind: Schedule",
    "tenant-volume-csi-hourly",
    "tenant-namespace-daily",
    "tenant-cluster-control-plane-daily",
    "storageLocation: primary-offsite",
    "volumeSnapshotLocations:",
    "snapshotVolumes: true",
    "defaultVolumesToFsBackup: false",
    "kubernetesclusterclaims.platform.privatecloud.local",
    "REPLACE_WITH_TENANT_NAMESPACE"
)

Require-Text "iac\kubernetes\production-backup\provider-backupplan-examples.yaml" @(
    "kind: BackupPlan",
    "kind: Volume",
    "kind: Namespace",
    "kind: KubernetesClusterClaim",
    "class: immutable",
    "class: remote",
    "locationRef: primary-offsite",
    "app-consistent"
)

Require-Text "iac\kubernetes\production-backup\restore-workflow-contract.yaml" @(
    "provider-production-backup-contract",
    "VirtualMachineClaim,Volume,Namespace,KubernetesClusterClaim",
    "Velero EnableCSI plus off-cell immutable object storage",
    "collisionPolicy",
    "approvalPolicy",
    "provider-velero-restore-templates",
    "kind: Restore",
    "namespaceMapping:",
    "tenant-cluster-restore.yaml"
)

Require-Text "gitops\platform-production-backup\kustomization.yaml" @(
    "../platform",
    "../../iac/kubernetes/production-cell/velero-backup-locations.yaml",
    "../../iac/kubernetes/production-backup"
)

Require-Text "docs\production-backup-dr.md" @(
    "Production Backup And Disaster Recovery",
    "Volume",
    "Namespace",
    "KubernetesClusterClaim",
    "object-store immutability",
    "runtime still needs an implementation"
)

$crds = Read-RepoText "iac\kubernetes\provider-api\crds.yaml"
foreach ($target in @(
    'enum: ["VirtualMachineClaim", "KubernetesClusterClaim", "Volume", "Namespace"]',
    'enum: ["local", "remote", "immutable"]',
    'kind: BackupPlan',
    'kind: RestoreRequest'
)) {
    if (-not $crds.Contains($target)) {
        throw "Provider API CRD does not expose expected backup/restore contract: $target"
    }
}

$labPlatform = Read-RepoText "gitops\platform\kustomization.yaml"
if ($labPlatform -match "production-backup|platform-production-backup") {
    throw "The shared lab platform overlay must not apply production backup by default."
}

$labCell = Read-RepoText "gitops\cells\lab-hyperv\kustomization.yaml"
if ($labCell -match "production-backup|platform-production-backup") {
    throw "The Hyper-V lab cell overlay must not apply production backup by default."
}

Write-Output "production_backup_blueprint_ok"
