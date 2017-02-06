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

function Require-Text {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string[]]$Patterns
    )
    $path = Require-File $RelativePath
    $text = Get-Content -LiteralPath $path -Raw
    foreach ($pattern in $Patterns) {
        if ($text -notmatch [regex]::Escape($pattern)) {
            throw "Missing pattern '$pattern' in $RelativePath"
        }
    }
}

Require-Text "iac\kubernetes\production-cell\kustomization.yaml" @(
    "namespaces.yaml",
    "rook-ceph-storage.yaml",
    "cilium-bgp-fabric.yaml",
    "velero-backup-locations.yaml"
)

Require-Text "iac\kubernetes\production-cell\rook-ceph-storage.yaml" @(
    "kind: CephCluster",
    "quay.io/ceph/ceph:v20.2.2",
    "kind: CephBlockPool",
    "failureDomain: rack",
    "kind: CephFilesystem",
    "kind: CephObjectStore",
    "REPLACE_WITH_STORAGE_NODE_A"
)

Require-Text "iac\kubernetes\production-cell\cilium-bgp-fabric.yaml" @(
    "kind: CiliumLoadBalancerIPPool",
    "kind: CiliumBGPClusterConfig",
    "kind: CiliumBGPPeerConfig",
    "kind: CiliumBGPAdvertisement",
    "LoadBalancerIP",
    "REPLACE_WITH_TOR_A_ADDRESS"
)

Require-Text "iac\kubernetes\production-cell\velero-backup-locations.yaml" @(
    "kind: BackupStorageLocation",
    "kind: VolumeSnapshotLocation",
    "kind: Schedule",
    "REPLACE_WITH_DEDICATED_BACKUP_BUCKET"
)

Require-Text "gitops\cells\production-cell-template\kustomization.yaml" @(
    "../../../iac/kubernetes/production-cell",
    "platform.privatecloud.local/cell-template: production"
)

$labOverlay = Get-Content -LiteralPath (Require-File "gitops\cells\lab-hyperv\kustomization.yaml") -Raw
if ($labOverlay -match "production-cell") {
    throw "The Hyper-V lab overlay must not reference the production-cell blueprint."
}

$platformOverlay = Get-Content -LiteralPath (Require-File "gitops\platform\kustomization.yaml") -Raw
if ($platformOverlay -match "production-cell") {
    throw "The shared platform overlay must not apply the production-cell blueprint by default."
}

Write-Output "production_cell_blueprint_ok"
