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

function Resolve-Python {
    $candidates = @()
    if ($env:PYTHON) {
        $candidates += $env:PYTHON
    }
    $candidates += @(
        "python3",
        "python",
        "C:\Users\yuri\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    )
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        $resolved = if ($command) { $command.Source } elseif (Test-Path -LiteralPath $candidate -PathType Leaf) { $candidate } else { $null }
        if ($resolved) {
            $previous = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            try {
                & $resolved --version 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    return $resolved
                }
            } finally {
                $ErrorActionPreference = $previous
            }
        }
    }
    throw "No Python interpreter found via PYTHON, python3, python, or bundled runtime."
}

function Require-Equal {
    param(
        [Parameter(Mandatory = $true)]$Actual,
        [Parameter(Mandatory = $true)]$Expected,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if ($Actual -ne $Expected) {
        throw "$Message Expected '$Expected', got '$Actual'."
    }
}

function Require-Contains {
    param(
        [Parameter(Mandatory = $true)][string[]]$Values,
        [Parameter(Mandatory = $true)][string]$Expected,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if ($Expected -notin $Values) {
        throw "$Message Missing '$Expected'."
    }
}

function Require-NoRegex {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $path = Require-File $RelativePath
    $text = Get-Content -LiteralPath $path -Raw
    if ($text -match $Pattern) {
        throw $Message
    }
}

$scriptRelative = "iac\scripts\production-backup-runtime-live-adapter.py"
$scriptPath = Require-File $scriptRelative
$python = Resolve-Python
$fixturePath = Join-Path ([System.IO.Path]::GetTempPath()) ("provider-backup-runtime-live-adapter-" + [System.Guid]::NewGuid().ToString("N") + ".json")

& $python -m py_compile $scriptPath
if ($LASTEXITCODE -ne 0) {
    throw "py_compile failed for $scriptRelative"
}
Write-Output "python_py_compile_ok"

$fixtureJson = @'
{
  "preflight": {
    "backupStorageLocation": "primary-offsite",
    "volumeSnapshotLocation": "primary-csi",
    "backupRepository": "tenant-a-primary-offsite",
    "volumeSnapshotClass": "provider-production-csi-retain",
    "canaryScope": "provider-backup-runtime-canary"
  },
  "cases": [
    {"name":"volume","backupPlan":{"name":"canary-volume-hourly","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Volume","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"canary-volume-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Volume","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"namespace","backupPlan":{"name":"canary-namespace-daily","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Namespace","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"canary-namespace-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Namespace","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"tenant-cluster","backupPlan":{"name":"canary-tenant-cluster-daily","namespace":"tenant-a","tenant":"tenant-a","targetKind":"KubernetesClusterClaim","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"canary-tenant-cluster-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"KubernetesClusterClaim","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"missing-malformed-preflight","preflight":{"backupStorageLocation":"primary-offsite"},"backupPlan":{"name":"bad-preflight","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Volume","schedule":"0 * * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"bad-preflight-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Volume","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"canary-scope-mismatch","backupPlan":{"name":"wrong-scope","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Volume","schedule":"0 * * * *","canaryScope":"production"},"restoreRequest":{"name":"wrong-scope-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Volume","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"cross-tenant-restore-without-approval","backupPlan":{"name":"cross-tenant","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Volume","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"cross-tenant-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-b","targetKind":"Volume","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"missing-restore-safety-controls","backupPlan":{"name":"missing-policy","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Namespace","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"missing-restore-safety-controls","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Namespace","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[],"resourcePolicyRef":"","resourceModifierRefs":[],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"target-collision","backupPlan":{"name":"collision","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Volume","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"target-collision","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Volume","mode":"Copy","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":true}},
    {"name":"unapproved-in-place-namespace-restore","backupPlan":{"name":"in-place-namespace","namespace":"tenant-a","tenant":"tenant-a","targetKind":"Namespace","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"in-place-namespace-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Namespace","mode":"InPlace","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"unapproved-in-place-tenant-cluster-restore","backupPlan":{"name":"in-place-cluster","namespace":"tenant-a","tenant":"tenant-a","targetKind":"KubernetesClusterClaim","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"in-place-cluster-restore","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"KubernetesClusterClaim","mode":"InPlace","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}},
    {"name":"malformed-provider-fixture","backupPlan":{"name":"malformed-provider-fixture","namespace":"tenant-a","tenant":"tenant-a","schedule":"0 */6 * * *","canaryScope":"provider-backup-runtime-canary"},"restoreRequest":{"name":"malformed-provider-fixture","namespace":"tenant-a","sourceTenant":"tenant-a","targetTenant":"tenant-a","targetKind":"Volume","canaryScope":"provider-backup-runtime-canary","namespaceMapping":[{"from":"tenant-a","to":"tenant-a"}],"resourcePolicyRef":"tenant-safe-restore-policy","resourceModifierRefs":["tenant-namespace-rewrite"],"providerApproved":false,"allowCrossTenant":false,"targetExists":false}}
  ]
}
'@
[System.IO.File]::WriteAllText($fixturePath, $fixtureJson, [System.Text.UTF8Encoding]::new($false))

$output = & $python $scriptPath $fixturePath
if ($LASTEXITCODE -ne 0) {
    throw "Adapter execution failed for $scriptRelative"
}

$jsonLine = $output | Where-Object { $_.StartsWith("ADAPTER_JSON:") } | Select-Object -First 1
if (-not $jsonLine) {
    throw "Adapter did not emit ADAPTER_JSON."
}
$payload = $jsonLine.Substring("ADAPTER_JSON:".Length) | ConvertFrom-Json

foreach ($marker in @(
    "provider_fixture_parse_ok",
    "velero_live_adapter_actions_ok",
    "live_adapter_status_patches_ok",
    "live_adapter_fail_closed_ok",
    "live_adapter_no_cluster_access_ok",
    "lab_overlay_no_live_adapter_reference_ok",
    "production_backup_runtime_live_adapter_ok"
)) {
    if ($marker -notin $output) {
        throw "Adapter output missing marker: $marker"
    }
}
Write-Output "provider_fixture_parse_ok"

Require-Equal $payload.adapterMode "disabled-by-default-live-adapter-prototype" "Adapter mode mismatch."
Require-Equal $payload.inputMode "json-fixtures" "Adapter did not use JSON fixture input mode."
Require-Equal $payload.preflightGate.canaryScope "provider-backup-runtime-canary" "Canary preflight scope mismatch."
Require-Equal $payload.preflightGate.failClosed $true "Preflight fail-closed flag mismatch."
Require-Equal $payload.happyPath.Count 3 "Happy path target count mismatch."

$targetKinds = @($payload.happyPath | ForEach-Object { $_.targetKind })
foreach ($kind in @("Volume", "Namespace", "KubernetesClusterClaim")) {
    Require-Contains $targetKinds $kind "Happy path target set is incomplete."
}

$allVeleroKinds = @($payload.happyPath | ForEach-Object { $_.veleroManifests } | ForEach-Object { $_.kind })
foreach ($kind in @("Schedule", "Backup", "Restore")) {
    Require-Equal (@($allVeleroKinds | Where-Object { $_ -eq $kind }).Count) 3 "Velero $kind count mismatch."
}
foreach ($scenario in $payload.happyPath) {
    Require-Equal $scenario.veleroManifests.Count 3 "Each happy path must emit Schedule, Backup, and Restore."
    Require-Equal $scenario.providerStatus.Count 2 "Each happy path must emit BackupPlan and RestoreRequest status."
    $kinds = @($scenario.veleroManifests | ForEach-Object { $_.kind })
    foreach ($kind in @("Schedule", "Backup", "Restore")) {
        Require-Contains $kinds $kind "Happy path Velero action set is incomplete."
    }
    Require-Equal $scenario.preflight.backupStorageLocation "primary-offsite" "BackupStorageLocation mismatch."
    Require-Equal $scenario.preflight.volumeSnapshotLocation "primary-csi" "VolumeSnapshotLocation mismatch."
    Require-Equal $scenario.preflight.backupRepository "tenant-a-primary-offsite" "BackupRepository mismatch."
    Require-Equal $scenario.preflight.volumeSnapshotClass "provider-production-csi-retain" "VolumeSnapshotClass mismatch."
}
Write-Output "velero_live_adapter_actions_ok"

$happyPhases = @($payload.happyPath | ForEach-Object { $_.providerStatus } | ForEach-Object { $_.phase })
Require-Equal (@($happyPhases | Where-Object { $_ -eq "Protected" }).Count) 3 "Protected status count mismatch."
Require-Equal (@($happyPhases | Where-Object { $_ -eq "Succeeded" }).Count) 3 "Succeeded status count mismatch."
Write-Output "live_adapter_status_patches_ok"

$expectedReasons = @(
    "PreflightUnavailableOrMalformed",
    "CanaryScopeMismatch",
    "CrossTenantRestoreDenied",
    "NamespaceMappingResourcePolicyOrModifierMissing",
    "TargetCollision",
    "InPlaceNamespaceRestoreApprovalMissing",
    "InPlaceTenantClusterRestoreApprovalMissing",
    "MalformedProviderFixture"
)
Require-Equal $payload.failClosed.Count 8 "Fail-closed scenario count mismatch."
foreach ($scenario in $payload.failClosed) {
    Require-Equal $scenario.veleroManifests.Count 0 "Fail-closed scenario emitted Velero manifests."
    Require-Equal $scenario.providerStatus.Count 1 "Fail-closed scenario should emit exactly one status."
    $phase = $scenario.providerStatus[0].phase
    if ($phase -notin @("FailedValidation", "Rejected", "Degraded")) {
        throw "Fail-closed phase must be FailedValidation, Rejected, or Degraded; got '$phase'."
    }
}
$actualReasons = @($payload.failClosed | ForEach-Object { $_.providerStatus[0].reason })
foreach ($reason in $expectedReasons) {
    Require-Contains $actualReasons $reason "Fail-closed reason set is incomplete."
}
Write-Output "live_adapter_fail_closed_ok"

Require-Equal $payload.clusterAccess.mode "offline" "Cluster access mode mismatch."
Require-Equal $payload.clusterAccess.commandsInvoked.Count 0 "Adapter must not invoke commands."
Require-Equal $payload.clusterAccess.networkClients.Count 0 "Adapter must not use network clients."
Require-Equal $payload.clusterAccess.configFilesRead.Count 0 "Adapter must not read cluster config files."

$scriptText = Get-Content -LiteralPath $scriptPath -Raw
foreach ($pattern in @(
    '(?im)^\s*(from|import)\s+kubernetes\b',
    '(?im)^\s*(from|import)\s+requests\b',
    '(?im)^\s*(from|import)\s+httpx2?\b',
    '(?im)^\s*(from|import)\s+urllib\b',
    '(?im)^\s*(from|import)\s+socket\b',
    '(?im)^\s*(from|import)\s+subprocess\b',
    'kubectl',
    '(?i)kubeconfig',
    '\.kube',
    'load_kube_config'
)) {
    if ($scriptText -match $pattern) {
        throw "Adapter source contains forbidden cluster, network, or process token for pattern: $pattern"
    }
}
Write-Output "live_adapter_no_cluster_access_ok"

$runtimePattern = "production-backup-runtime-live-adapter|live-adapter|provider-backup-runtime-controller|production-backup-runtime"
Require-NoRegex "gitops\platform\kustomization.yaml" $runtimePattern "The shared lab platform overlay must not reference the live adapter or runtime."
Require-NoRegex "gitops\cells\lab-hyperv\kustomization.yaml" $runtimePattern "The Hyper-V lab overlay must not reference the live adapter or runtime."
Write-Output "lab_overlay_no_live_adapter_reference_ok"
Write-Output "production_backup_runtime_live_adapter_ok"
Remove-Item -LiteralPath $fixturePath -Force -ErrorAction SilentlyContinue
