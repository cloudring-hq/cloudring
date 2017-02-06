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
    if ($null -eq $Value) { return "" }
    $normalized = $Value.Trim()
    if ($normalized.Length -ge 2 -and $normalized.StartsWith('"') -and $normalized.EndsWith('"')) {
        return $normalized.Substring(1, $normalized.Length - 2)
    }
    return $normalized
}

function Get-TopLevelMap {
    param([string]$Document, [string]$Section)
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
        if ($inSection -and $line -match "^[A-Za-z0-9_-]+:") { break }
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
    param([string]$Document, [string]$Parent, [string]$Child)
    $map = @{}
    $lines = $Document -split "`r?`n"
    $inParent = $false
    $inChild = $false
    foreach ($line in $lines) {
        if ($line -match "^$([regex]::Escape($Parent)):\s*$") {
            $inParent = $true
            continue
        }
        if ($inParent -and $line -match "^[A-Za-z0-9_-]+:") { break }
        if ($inParent -and $line -match "^\s{2}$([regex]::Escape($Child)):\s*$") {
            $inChild = $true
            continue
        }
        if ($inChild -and $line -match "^\s{2}[A-Za-z0-9_.\/-]+:") { break }
        if ($inChild -and $line -match "^\s{4}([A-Za-z0-9_.\/-]+):\s*(.*)$") {
            $map[$Matches[1]] = Normalize-YamlScalar $Matches[2]
        }
    }
    return $map
}

function Get-ConfigMapDocumentFromText {
    param([string]$Text, [string]$Name)
    $docs = $Text -split "(?m)^---\s*$"
    foreach ($doc in $docs) {
        if ([string]::IsNullOrWhiteSpace($doc)) { continue }
        if ($doc -notmatch "(?m)^kind:\s*ConfigMap\s*$") { continue }
        $metadata = Get-TopLevelMap $doc "metadata"
        if ($metadata.ContainsKey("name") -and $metadata["name"] -eq $Name) {
            return $doc
        }
    }
    throw "ConfigMap $Name not found"
}

function Get-ConfigMapDocument {
    param([string]$RelativePath, [string]$Name)
    return Get-ConfigMapDocumentFromText (Read-RepoText $RelativePath) $Name
}

function Require-DataValue {
    param([hashtable]$Data, [string]$Key, [string]$Expected)
    if (-not $Data.ContainsKey($Key)) { throw "Missing data key $Key" }
    if ($Data[$Key] -ne $Expected) {
        throw "Unexpected value for $Key. Expected '$Expected', got '$($Data[$Key])'"
    }
}

function Require-DataContains {
    param([hashtable]$Data, [string]$Key, [string]$ExpectedSubstring)
    if (-not $Data.ContainsKey($Key)) { throw "Missing data key $Key" }
    if (-not $Data[$Key].Contains($ExpectedSubstring)) {
        throw "Missing '$ExpectedSubstring' in data key $Key"
    }
}

function Require-DataListContains {
    param([hashtable]$Data, [string]$Key, [string[]]$ExpectedItems)
    if (-not $Data.ContainsKey($Key)) { throw "Missing data key $Key" }
    $items = @($Data[$Key].Split(",") | ForEach-Object { $_.Trim() })
    foreach ($expected in $ExpectedItems) {
        if ($items -notcontains $expected) {
            throw "Missing list item '$expected' in data key $Key"
        }
    }
}

function Require-DataOrderedList {
    param([hashtable]$Data, [string]$Key, [string[]]$ExpectedItems)
    if (-not $Data.ContainsKey($Key)) { throw "Missing data key $Key" }
    $items = @($Data[$Key].Split(",") | ForEach-Object { $_.Trim() })
    if ($items.Count -ne $ExpectedItems.Count) {
        throw "Unexpected item count for $Key"
    }
    for ($i = 0; $i -lt $ExpectedItems.Count; $i++) {
        if ($items[$i] -ne $ExpectedItems[$i]) {
            throw "Unsafe ordering for $Key at index $i. Expected '$($ExpectedItems[$i])', got '$($items[$i])'"
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
    if (-not (Test-Path -LiteralPath $rootPath)) { throw "Missing path for boundary scan: $RelativePath" }
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

function Invoke-ContractChecks {
    param([string]$Text)

    $contractDoc = Get-ConfigMapDocumentFromText $Text "provider-backup-service-runtime-integration-contract"
    $drillDoc = Get-ConfigMapDocumentFromText $Text "provider-backup-service-runtime-integration-drill"
    $data = Get-TopLevelMap $contractDoc "data"
    $annotations = Get-NestedMap $contractDoc "metadata" "annotations"
    $drillData = Get-TopLevelMap $drillDoc "data"
    $drillAnnotations = Get-NestedMap $drillDoc "metadata" "annotations"

    Require-DataValue $annotations "platform.privatecloud.local/template-only" "true"
    Require-DataValue $annotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
    Require-DataValue $annotations "platform.privatecloud.local/backup-service-runtime-integration-contract" "v1"
    Require-DataValue $drillAnnotations "platform.privatecloud.local/template-only" "true"
    Require-DataValue $drillAnnotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
    Require-DataValue $data "owner" "provider-backup-runtime-controller"
    Require-DataValue $data "mode-default" "disabled"
    Require-DataValue $data "leader-election-lease" "provider-backup-runtime-controller"
    Require-DataListContains $data "target-kinds" @("Volume", "Namespace", "KubernetesClusterClaim")
    Require-DataContains $data "target-mapping" "Volume=Velero Backup plus CSI VolumeSnapshot"
    Require-DataContains $data "target-mapping" "Namespace=Velero namespace/resource filter"
    Require-DataContains $data "target-mapping" "KubernetesClusterClaim=provider claim plus CAPI/CAPK resources"
    Require-DataListContains $data "secret-refs" @(
        "platform-system/provider-backup-runtime-object-store",
        "platform-system/provider-backup-runtime-repository-keys",
        "platform-system/provider-backup-runtime-restore-approval-key"
    )
    Require-DataContains $data "object-store-wiring" "BackupStorageLocation=primary-offsite"
    Require-DataContains $data "object-store-wiring" "VolumeSnapshotLocation=csi-primary"
    Require-DataContains $data "object-store-wiring" "BackupRepository=per-tenant-namespace"
    Require-DataContains $data "object-store-wiring" "VolumeSnapshotClass=provider-production-csi-retain"
    Require-DataContains $data "object-store-wiring" "credentialsSecret=platform-system/provider-backup-runtime-object-store"
    Require-DataContains $data "immutable-storage" "ObjectLock=required"
    Require-DataContains $data "immutable-storage" "Versioning=required"
    Require-DataContains $data "immutable-storage" "DeleteDeny=required"
    Require-DataContains $data "immutable-storage" "TenantWriteCredentials=forbidden"
    Require-DataOrderedList $data "restore-phases" @(
        "request-accepted",
        "preflight-gates",
        "source-lock",
        "restore-plan",
        "canary-restore",
        "integrity-check",
        "promotion",
        "post-restore-audit",
        "cleanup"
    )
    Require-DataListContains $data "preflight-gates" @(
        "runtimeEnabled",
        "ownerLeaseHeld",
        "objectStoreSecretPresent",
        "BackupStorageLocationAvailable",
        "VolumeSnapshotLocationReachable",
        "BackupRepositoryReady",
        "VolumeSnapshotClassRetain",
        "immutableStorageEnabled",
        "tenantAuthorizationPassed",
        "sourceBackupVisible",
        "targetNamespaceOwned",
        "quotaAndCollisionCheckPassed",
        "restorePolicyApproved"
    )
    Require-DataListContains $data "status-conditions" @(
        "BackupServiceRuntimeReady",
        "RestorePreflightPassed",
        "RestorePlanReady",
        "RestoreCanaryPassed",
        "RestoreIntegrityPassed",
        "RestorePromoted",
        "RestoreRejected",
        "ImmutableStorageVerified",
        "TenantIsolationVerified"
    )
    Require-DataListContains $data "audit-events" @(
        "BackupRuntimeIntegrationAccepted",
        "BackupRuntimeIntegrationRejected",
        "RestorePreflightStarted",
        "RestorePreflightFailed",
        "RestorePreflightPassed",
        "RestoreCanaryCreated",
        "RestoreIntegrityPassed",
        "RestorePromoted",
        "RestoreTenantIsolationRejected",
        "ImmutableStoragePolicyRejected"
    )
    Require-DataListContains $data "slo-metrics" @(
        "backup_runtime_backup_success_rate",
        "backup_runtime_restore_success_rate",
        "backup_runtime_restore_rto_seconds",
        "backup_runtime_backup_freshness_seconds",
        "backup_runtime_repository_errors_total",
        "backup_runtime_cross_tenant_denied_total",
        "backup_runtime_immutability_failures_total"
    )
    Require-DataListContains $data "alert-rules" @(
        "BackupRuntimeDown",
        "BackupRuntimeObjectStoreSecretMissing",
        "BackupRuntimeImmutableStorageMissing",
        "BackupRuntimeRestoreErrorBudgetBurn",
        "BackupRuntimeRtoHigh",
        "BackupRuntimeRepositoryErrorsHigh",
        "BackupRuntimeCrossTenantRestoreAttempt"
    )
    Require-DataContains $data "tenant-isolation-rules" "sourceProjectRef must equal targetProjectRef"
    Require-DataContains $data "tenant-isolation-rules" "tenant namespaces never receive object-store credentials"
    Require-DataContains $data "tenant-isolation-rules" "cluster-scoped restore resources require provider policy allowlist"
    Require-DataContains $data "failure-policy" "missing owner"
    Require-DataContains $data "failure-policy" "missing object-store secret"
    Require-DataContains $data "failure-policy" "mutable bucket policy"
    Require-DataContains $data "failure-policy" "unsafe restore phase order"
    Require-DataContains $data "failure-policy" "cross-tenant restore target"
    Require-DataContains $data "failure-policy" "missing status condition"
    Require-DataContains $data "failure-policy" "missing audit event"
    Require-DataContains $data "failure-policy" "missing SLO hook"
    Require-DataContains $drillData "drill" "platform-system/provider-backup-runtime-object-store"
    Require-DataContains $drillData "drill" "ObjectLock=required"
    Require-DataContains $drillData "drill" "Volume targets"
    Require-DataContains $drillData "drill" "Namespace targets"
    Require-DataContains $drillData "drill" "KubernetesClusterClaim targets"
    Require-DataContains $drillData "drill" "Cross-tenant restore attempts must emit RestoreTenantIsolationRejected"
    Require-DataContains $drillData "drill" "Mutable bucket policy must emit ImmutableStoragePolicyRejected"
}

$contractPath = "iac\kubernetes\production-backup-runtime\service-runtime-integration-contract.yaml"
Require-Text "iac\kubernetes\production-backup-runtime\kustomization.yaml" @("service-runtime-integration-contract.yaml")
$contractText = Read-RepoText $contractPath
Invoke-ContractChecks $contractText
Write-Output "production_backup_service_runtime_integration_contract_ok"

$runtimePattern = "service-runtime-integration-contract.yaml|provider-backup-service-runtime-integration-contract|provider-backup-service-runtime-integration-drill|backup-service-runtime-integration|verify-production-backup-service-runtime-integration|backup_runtime_cross_tenant_denied_total|BackupRuntimeImmutableStorageMissing"
Require-TreeNoRegex "gitops\platform" $runtimePattern "The shared lab platform overlay must not apply backup service runtime integration resources."
Require-TreeNoRegex "gitops\cells\lab-hyperv" $runtimePattern "The Hyper-V lab cell overlay must not apply backup service runtime integration resources."
Require-TreeNoRegex "iac\kubernetes\production-backup" $runtimePattern "The contract-only backup blueprint must not include backup service runtime integration resources."
Require-TreeNoRegex "gitops\platform-production-backup" $runtimePattern "The contract-only backup overlay must not include backup service runtime integration resources."
Write-Output "lab_overlay_no_backup_service_runtime_integration_reference_ok"

$negativeCases = @(
    @{ Name = "missing_owner"; Text = $contractText.Replace("owner: provider-backup-runtime-controller", "owner: missing-controller") },
    @{ Name = "missing_object_store_secret"; Text = $contractText.Replace("platform-system/provider-backup-runtime-object-store", "platform-system/missing-object-store") },
    @{ Name = "mutable_bucket"; Text = $contractText.Replace("ObjectLock=required", "ObjectLock=optional") },
    @{ Name = "unsafe_restore_phase_order"; Text = $contractText.Replace("request-accepted,preflight-gates,source-lock,restore-plan,canary-restore,integrity-check,promotion,post-restore-audit,cleanup", "request-accepted,restore-plan,preflight-gates,source-lock,canary-restore,integrity-check,promotion,post-restore-audit,cleanup") },
    @{ Name = "cross_tenant_restore_target"; Text = $contractText.Replace("sourceProjectRef must equal targetProjectRef", "sourceProjectRef may differ from targetProjectRef") },
    @{ Name = "missing_status_audit"; Text = $contractText.Replace("RestoreTenantIsolationRejected", "RestoreTenantIsolationMissing") },
    @{ Name = "missing_slo_hook"; Text = $contractText.Replace("backup_runtime_cross_tenant_denied_total", "backup_runtime_cross_tenant_metric_missing") }
)

foreach ($case in $negativeCases) {
    $failed = $false
    try {
        Invoke-ContractChecks $case.Text
    } catch {
        $failed = $true
    }
    if (-not $failed) {
        throw "Negative probe did not fail: $($case.Name)"
    }
}

$spoofText = $contractText.Replace("name: provider-backup-service-runtime-integration-contract", "name: metadata-spoof-probe").Replace("owner: provider-backup-runtime-controller", "metadata:`n  name: provider-backup-runtime-controller")
$spoofFailed = $false
try { Invoke-ContractChecks $spoofText } catch { $spoofFailed = $true }
if (-not $spoofFailed) { throw "negative_metadata_spoof_probe did not fail" }

$commentText = $contractText.Replace("BackupRuntimeImmutableStorageMissing", "# BackupRuntimeImmutableStorageMissing")
$commentFailed = $false
try { Invoke-ContractChecks $commentText } catch { $commentFailed = $true }
if (-not $commentFailed) { throw "negative_comment_probe did not fail" }

Write-Output "production_backup_service_runtime_integration_fail_closed_ok"

Require-Text "docs\production-backup-operations.md" @(
    "Production Backup Service Runtime Integration",
    "verify-production-backup-service-runtime-integration.ps1",
    "provider-backup-service-runtime-integration-contract",
    "RestoreTenantIsolationRejected",
    "backup_runtime_cross_tenant_denied_total"
)

Require-Text "docs\production-backup-dr.md" @(
    "service-runtime-integration-contract.yaml",
    "BackupRuntimeImmutableStorageMissing",
    "immutable storage"
)

Require-Text "iac\kubernetes\production-backup-runtime\README.md" @(
    "Service Runtime Integration Contract",
    "verify-production-backup-service-runtime-integration.ps1",
    "provider-backup-service-runtime-integration-contract"
)

Require-Text "docs\provider-roadmap.md" @(
    "Add production backup service runtime integration contract",
    "verify-production-backup-service-runtime-integration.ps1"
)

Require-Text "docs\test-plan.md" @(
    "Production backup service runtime integration contract",
    "verify-production-backup-service-runtime-integration.ps1"
)

Require-Text "docs\operations-log.md" @(
    "Production backup service runtime integration contract",
    "verify-production-backup-service-runtime-integration.ps1"
)

Write-Output "production_backup_service_runtime_integration_ok"
