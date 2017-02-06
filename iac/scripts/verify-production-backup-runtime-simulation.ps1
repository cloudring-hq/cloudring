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
        $resolved = $null
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            $resolved = $command.Source
        } elseif (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $resolved = $candidate
        }

        if ($resolved) {
            $previousErrorActionPreference = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            try {
                & $resolved --version 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    return $resolved
                }
            } finally {
                $ErrorActionPreference = $previousErrorActionPreference
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

$scriptRelative = "iac\scripts\simulate-production-backup-runtime-canary.py"
$scriptPath = Require-File $scriptRelative
$python = Resolve-Python

& $python -m py_compile $scriptPath
if ($LASTEXITCODE -ne 0) {
    throw "py_compile failed for $scriptRelative"
}
Write-Output "python_py_compile_ok"

$output = & $python $scriptPath
if ($LASTEXITCODE -ne 0) {
    throw "Simulation failed for $scriptRelative"
}

$jsonLine = $output | Where-Object { $_.StartsWith("SIMULATION_JSON:") } | Select-Object -First 1
if (-not $jsonLine) {
    throw "Simulation did not emit SIMULATION_JSON."
}

$jsonText = $jsonLine.Substring("SIMULATION_JSON:".Length)
$payload = $jsonText | ConvertFrom-Json

$markers = @(
    "velero_backup_actions_ok",
    "velero_restore_actions_ok",
    "fail_closed_boundary_ok",
    "no_cluster_access_ok",
    "production_backup_runtime_canary_simulation_ok"
)
foreach ($marker in $markers) {
    if ($marker -notin $output) {
        throw "Simulation output missing marker: $marker"
    }
}

$targetKinds = @($payload.happyPath | ForEach-Object { $_.targetKind })
Require-Contains $targetKinds "Volume" "Happy path target set is incomplete."
Require-Contains $targetKinds "Namespace" "Happy path target set is incomplete."
Require-Contains $targetKinds "KubernetesClusterClaim" "Happy path target set is incomplete."

Require-Equal $payload.happyPath.Count 3 "Happy path scenario count mismatch."
foreach ($scenario in $payload.happyPath) {
    Require-Equal $scenario.veleroActions.Count 3 "Each happy path must emit Schedule, Backup, and Restore."
    Require-Equal $scenario.statusActions.Count 2 "Each happy path must emit BackupPlan and RestoreRequest status."
    $kinds = @($scenario.veleroActions | ForEach-Object { $_.kind })
    Require-Contains $kinds "Schedule" "Missing Velero Schedule action."
    Require-Contains $kinds "Backup" "Missing Velero Backup action."
    Require-Contains $kinds "Restore" "Missing Velero Restore action."
}

$allVeleroKinds = @($payload.happyPath | ForEach-Object { $_.veleroActions } | ForEach-Object { $_.kind })
Require-Equal (@($allVeleroKinds | Where-Object { $_ -eq "Schedule" }).Count) 3 "Schedule action count mismatch."
Require-Equal (@($allVeleroKinds | Where-Object { $_ -eq "Backup" }).Count) 3 "Backup action count mismatch."
Write-Output "velero_backup_actions_ok"

Require-Equal (@($allVeleroKinds | Where-Object { $_ -eq "Restore" }).Count) 3 "Restore action count mismatch."
$statusPhases = @($payload.happyPath | ForEach-Object { $_.statusActions } | ForEach-Object { $_.phase })
Require-Equal (@($statusPhases | Where-Object { $_ -eq "Protected" }).Count) 3 "Protected status count mismatch."
Require-Equal (@($statusPhases | Where-Object { $_ -eq "Succeeded" }).Count) 3 "Succeeded status count mismatch."
Write-Output "velero_restore_actions_ok"

Require-Equal $payload.preflight.backupStorageLocation "primary-offsite" "BackupStorageLocation preflight mismatch."
Require-Equal $payload.preflight.volumeSnapshotLocation "primary-csi" "VolumeSnapshotLocation preflight mismatch."
Require-Equal $payload.preflight.backupRepository "tenant-a-primary-offsite" "BackupRepository preflight mismatch."
Require-Equal $payload.preflight.volumeSnapshotClass "provider-production-csi-retain" "VolumeSnapshotClass preflight mismatch."
Require-Equal $payload.preflight.canaryScope "provider-backup-runtime-canary" "Canary scope preflight mismatch."

$expectedReasons = @(
    "PreflightUnavailableOrMalformed",
    "CrossTenantRestoreDenied",
    "NamespaceMappingResourcePolicyOrModifierMissing",
    "TargetCollision",
    "InPlaceNamespaceRestoreApprovalMissing",
    "InPlaceTenantClusterRestoreApprovalMissing"
)
Require-Equal $payload.failClosed.Count 6 "Fail-closed scenario count mismatch."
foreach ($scenario in $payload.failClosed) {
    Require-Equal $scenario.veleroActions.Count 0 "Fail-closed scenario emitted Velero actions."
    Require-Equal $scenario.statusActions.Count 1 "Fail-closed scenario should emit exactly one status."
    $phase = $scenario.statusActions[0].phase
    if ($phase -notin @("Rejected", "Degraded")) {
        throw "Fail-closed status must be Rejected or Degraded, got '$phase'."
    }
}
$actualReasons = @($payload.failClosed | ForEach-Object { $_.statusActions[0].reason })
foreach ($reason in $expectedReasons) {
    Require-Contains $actualReasons $reason "Fail-closed reason set is incomplete."
}
Write-Output "fail_closed_boundary_ok"

Require-Equal $payload.clusterAccess.mode "offline" "Cluster access mode mismatch."
Require-Equal $payload.clusterAccess.readConfig $false "Simulator must not read cluster config."
Require-Equal $payload.clusterAccess.commandsInvoked.Count 0 "Simulator must not invoke cluster commands."
Require-Equal $payload.clusterAccess.networkClients.Count 0 "Simulator must not use network clients."

$scriptText = Get-Content -LiteralPath $scriptPath -Raw
$forbiddenPatterns = @(
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
)
foreach ($pattern in $forbiddenPatterns) {
    if ($scriptText -match $pattern) {
        throw "Simulator source contains forbidden cluster or network access token for pattern: $pattern"
    }
}
Write-Output "no_cluster_access_ok"
Write-Output "production_backup_runtime_canary_simulation_ok"
